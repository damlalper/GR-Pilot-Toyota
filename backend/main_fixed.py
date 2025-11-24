from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import Optional, List
import os
import sys
from groq import Groq

# Add src directory to path for MultiDatasetLoader
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# ML Models import
try:
    from ml.anomaly_model import DrivingAnomalyDetector
    from ml.lap_predictor import LapTimePredictor
    from ml.driver_clustering import DriverStyleClusterer
    from ml.feature_engineering import LapFeatureAggregator, TelemetryFeatureEngineer
    from data.multi_dataset_loader import MultiDatasetLoader
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"ML modules not available - using fallback methods: {e}")

app = FastAPI(title="GR-Pilot API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths - Circuit of the Americas
COTA_BASE_DIR = r"C:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA"
DATA_DIR = os.path.join(COTA_BASE_DIR, "Race 2")
TELEMETRY_PATH = os.path.join(DATA_DIR, "R2_cota_telemetry_data.csv")
WEATHER_PATH = os.path.join(DATA_DIR, "26_Weather_ Race 2_Anonymized.CSV")
SECTORS_PATH = os.path.join(DATA_DIR, "23_AnalysisEnduranceWithSections_ Race 2_Anonymized.CSV")
LAP_TIMES_PATH = os.path.join(DATA_DIR, "COTA_lap_time_R2.csv")
BEST_LAPS_PATH = os.path.join(DATA_DIR, "99_Best 10 Laps By Driver_ Race 2_Anonymized.CSV")

# Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Multi-dataset loader (loads all 10 datasets)
multi_loader = None
if ML_AVAILABLE:
    try:
        multi_loader = MultiDatasetLoader(base_dir=COTA_BASE_DIR)
        print("MultiDatasetLoader initialized")
    except Exception as e:
        print(f"MultiDatasetLoader initialization failed: {e}")

# Feature engineer
feature_engineer = None
if ML_AVAILABLE:
    try:
        feature_engineer = TelemetryFeatureEngineer()
        print("TelemetryFeatureEngineer initialized")
    except Exception as e:
        print(f"FeatureEngineer initialization failed: {e}")

# Cache
cached_data = {}

# ML Models cache
ml_models = {
    'anomaly_detector': None,
    'lap_predictor': None,
    'driver_clusterer': None
}

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml", "trained_models")

def load_ml_models():
    """Load trained ML models if available."""
    global ml_models

    if not ML_AVAILABLE:
        return

    # Load Anomaly Detector
    anomaly_path = os.path.join(MODELS_DIR, "anomaly_detector.pkl")
    if os.path.exists(anomaly_path) and ml_models['anomaly_detector'] is None:
        try:
            ml_models['anomaly_detector'] = DrivingAnomalyDetector()
            ml_models['anomaly_detector'].load(anomaly_path)
            print("[OK] Anomaly detector loaded")
        except Exception as e:
            print(f"[FAIL] Failed to load anomaly detector: {e}")

    # Load Lap Predictor
    predictor_path = os.path.join(MODELS_DIR, "lap_predictor.pkl")
    if os.path.exists(predictor_path) and ml_models['lap_predictor'] is None:
        try:
            ml_models['lap_predictor'] = LapTimePredictor()
            ml_models['lap_predictor'].load(predictor_path)
            print("[OK] Lap predictor loaded")
        except Exception as e:
            print(f"[FAIL] Failed to load lap predictor: {e}")

    # Load Driver Clusterer
    clusterer_path = os.path.join(MODELS_DIR, "driver_clusterer.pkl")
    if os.path.exists(clusterer_path) and ml_models['driver_clusterer'] is None:
        try:
            ml_models['driver_clusterer'] = DriverStyleClusterer()
            ml_models['driver_clusterer'].load(clusterer_path)
            print("[OK] Driver clusterer loaded")
        except Exception as e:
            print(f"[FAIL] Failed to load driver clusterer: {e}")

def load_telemetry(nrows=500000):
    if "telemetry" in cached_data:
        return cached_data["telemetry"]

    try:
        df_raw = pd.read_csv(TELEMETRY_PATH, nrows=nrows)
        unique_vehicles = df_raw['vehicle_id'].unique()
        if len(unique_vehicles) > 0:
            df_raw = df_raw[df_raw['vehicle_id'] == unique_vehicles[0]]

        df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
        df_pivot = df_raw.pivot_table(
            index='timestamp',
            columns='telemetry_name',
            values='telemetry_value',
            aggfunc='first'
        )

        lap_series = df_raw.groupby('timestamp')['lap'].first()
        df_pivot = df_pivot.join(lap_series)
        df_pivot = df_pivot.ffill().dropna()
        df_pivot = df_pivot.reset_index()

        numeric_cols = ['speed', 'nmot', 'Steering_Angle', 'ath', 'pbrake_f', 'pbrake_r', 'accx_can', 'accy_can', 'gear']
        for col in numeric_cols:
            if col in df_pivot.columns:
                df_pivot[col] = pd.to_numeric(df_pivot[col], errors='coerce')

        if 'speed' in df_pivot.columns:
            df_pivot['time_delta'] = df_pivot['timestamp'].diff().dt.total_seconds().fillna(0)
            df_pivot['speed_ms'] = df_pivot['speed'] / 3.6
            df_pivot['distance_delta'] = df_pivot['speed_ms'] * df_pivot['time_delta']
            df_pivot['distance'] = df_pivot['distance_delta'].cumsum()

        # Enhanced Dead Reckoning using IMU (accx_can, accy_can) + GPS fallback
        if 'Steering_Angle' in df_pivot.columns and 'speed' in df_pivot.columns:
            # Method 1: Steering-based dead reckoning
            STEERING_FACTOR = 0.002
            v = df_pivot['speed'] / 3.6  # Convert to m/s
            delta = np.radians(df_pivot['Steering_Angle'])
            heading_change = delta * v * df_pivot['time_delta'] * STEERING_FACTOR
            df_pivot['heading'] = heading_change.cumsum()

            # Method 2: Enhanced with IMU data (if available)
            if 'accx_can' in df_pivot.columns and 'accy_can' in df_pivot.columns:
                # Use lateral acceleration to refine heading estimate
                lateral_acc = df_pivot['accy_can']  # Lateral G
                # Compensate heading with actual lateral acceleration
                heading_correction = np.arctan2(lateral_acc, 9.81) * 0.1  # Small correction factor
                df_pivot['heading'] = df_pivot['heading'] + heading_correction.cumsum()

            # Calculate position
            df_pivot['dx'] = v * np.cos(df_pivot['heading']) * df_pivot['time_delta']
            df_pivot['dy'] = v * np.sin(df_pivot['heading']) * df_pivot['time_delta']
            df_pivot['WorldPositionX'] = df_pivot['dx'].cumsum()
            df_pivot['WorldPositionY'] = df_pivot['dy'].cumsum()

            # Convert to lat/lon (COTA coordinates)
            COTA_LAT, COTA_LON = 30.1328, -97.6411  # COTA start/finish
            df_pivot['lat'] = COTA_LAT + (df_pivot['WorldPositionY'] / 111000)
            df_pivot['lon'] = COTA_LON + (df_pivot['WorldPositionX'] / 96000)

        cached_data["telemetry"] = df_pivot
        return df_pivot
    except Exception as e:
        print(f"Error loading telemetry: {e}")
        return pd.DataFrame()

def load_lap_times():
    if "lap_times" in cached_data:
        return cached_data["lap_times"]
    try:
        df = pd.read_csv(LAP_TIMES_PATH)
        cached_data["lap_times"] = df
        return df
    except:
        return pd.DataFrame()

def load_weather():
    if "weather" in cached_data:
        return cached_data["weather"]

    # Try MultiDatasetLoader first
    if multi_loader:
        try:
            df = multi_loader.load_weather_data(race='race2')
            cached_data["weather"] = df
            return df
        except Exception as e:
            print(f"MultiLoader weather failed: {e}")

    # Fallback to direct load
    try:
        df = pd.read_csv(WEATHER_PATH, sep=';')
        # Rename columns to standard names
        df = df.rename(columns={
            'AIR_TEMP': 'ambient_temp',
            'TRACK_TEMP': 'track_temp',
            'HUMIDITY': 'humidity',
            'WIND_SPEED': 'wind_speed',
            'WIND_DIRECTION': 'wind_direction',
            'RAIN': 'rain',
            'PRESSURE': 'pressure'
        })
        cached_data["weather"] = df
        return df
    except Exception as e:
        print(f"Error loading weather: {e}")
        return pd.DataFrame()

def load_sectors():
    if "sectors" in cached_data:
        return cached_data["sectors"]

    # Try MultiDatasetLoader first
    if multi_loader:
        try:
            df = multi_loader.load_sector_analysis(race='race2')
            cached_data["sectors"] = df
            return df
        except Exception as e:
            print(f"MultiLoader sectors failed: {e}")

    # Fallback to direct load
    try:
        df = pd.read_csv(SECTORS_PATH, sep=';')
        cached_data["sectors"] = df
        return df
    except Exception as e:
        print(f"Error loading sectors: {e}")
        return pd.DataFrame()

@app.on_event("startup")
async def startup_event():
    """Load ML models and datasets on startup."""
    print("\n=== GR-Pilot API Startup ===")

    # Load ML models
    load_ml_models()

    # Pre-load Multi-datasets
    if multi_loader:
        try:
            print("\nPre-loading datasets...")
            multi_loader.load_weather_data(race='race2')
            multi_loader.load_sector_analysis(race='race2')
            multi_loader.load_best_laps(race='race2')
            print("Datasets pre-loaded successfully")
        except Exception as e:
            print(f"Dataset pre-loading failed: {e}")

    print("=== Startup Complete ===\n")

@app.get("/")
def root():
    return {
        "message": "GR-Pilot API",
        "version": "2.0.0",
        "status": "running",
        "ml_models_loaded": {
            "anomaly_detector": ml_models['anomaly_detector'] is not None,
            "lap_predictor": ml_models['lap_predictor'] is not None,
            "driver_clusterer": ml_models['driver_clusterer'] is not None
        }
    }

@app.get("/api/telemetry")
def get_telemetry(lap: Optional[int] = None, sample: int = 100, enriched: bool = False):
    """
    Get telemetry data with optional feature engineering.

    Args:
        lap: Optional lap number filter
        sample: Number of samples to return
        enriched: If True, includes engineered features (rolling stats, derivatives, etc.)
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No telemetry data")

    if lap is not None:
        df = df[df['lap'] == lap].copy()
        if not df.empty:
            df['distance'] = df['distance'] - df['distance'].iloc[0]

    # Apply feature engineering if requested
    if enriched and feature_engineer:
        try:
            df = feature_engineer.extract_all_features(df)
        except Exception as e:
            print(f"Feature engineering failed: {e}")

    # Sample for performance
    if len(df) > sample:
        indices = np.linspace(0, len(df)-1, sample, dtype=int)
        df = df.iloc[indices]

    return df.to_dict(orient='records')

@app.get("/api/features/{lap}")
def get_lap_features(lap: int):
    """
    Get engineered features for a specific lap.
    Returns rolling stats, derivatives, braking patterns, etc.
    """
    if not feature_engineer:
        raise HTTPException(status_code=503, detail="Feature engineering not available")

    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    try:
        # Extract all features
        df_enriched = feature_engineer.extract_all_features(df_lap)

        # Get feature names (exclude original columns)
        original_cols = set(df_lap.columns)
        feature_cols = [c for c in df_enriched.columns if c not in original_cols]

        # Sample for performance
        if len(df_enriched) > 500:
            indices = np.linspace(0, len(df_enriched)-1, 500, dtype=int)
            df_enriched = df_enriched.iloc[indices]

        return {
            "lap": lap,
            "feature_count": len(feature_cols),
            "feature_names": feature_cols,
            "data": df_enriched[['distance'] + feature_cols[:20]].to_dict(orient='records')  # Top 20 features
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")

@app.get("/api/laps")
def get_laps():
    df = load_telemetry()
    if df.empty:
        return []
    return sorted(df['lap'].unique().tolist())

@app.get("/api/lap/{lap_number}")
def get_lap_data(lap_number: int, points: int = 500):
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap_number].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # Sample
    if len(df_lap) > points:
        indices = np.linspace(0, len(df_lap)-1, points, dtype=int)
        df_lap = df_lap.iloc[indices]

    cols = ['distance', 'speed', 'nmot', 'ath', 'pbrake_f', 'Steering_Angle', 'gear',
            'WorldPositionX', 'WorldPositionY', 'lat', 'lon', 'timestamp']
    available_cols = [c for c in cols if c in df_lap.columns]

    result = df_lap[available_cols].copy()
    result['timestamp'] = result['timestamp'].astype(str)

    return {
        "lap": lap_number,
        "points": len(result),
        "data": result.to_dict(orient='records'),
        "stats": {
            "max_speed": float(df_lap['speed'].max()),
            "avg_speed": float(df_lap['speed'].mean()),
            "max_rpm": float(df_lap['nmot'].max()) if 'nmot' in df_lap.columns else 0,
            "distance": float(df_lap['distance'].max())
        }
    }

@app.get("/api/track")
def get_track_data():
    df = load_telemetry()
    if df.empty or 'WorldPositionX' not in df.columns:
        raise HTTPException(status_code=404, detail="No track data")

    # Get one full lap for track outline
    laps = df['lap'].unique()
    if len(laps) == 0:
        raise HTTPException(status_code=404, detail="No laps")

    df_lap = df[df['lap'] == laps[0]].copy()

    # Sample for track outline
    if len(df_lap) > 200:
        indices = np.linspace(0, len(df_lap)-1, 200, dtype=int)
        df_lap = df_lap.iloc[indices]

    return {
        "track": df_lap[['WorldPositionX', 'WorldPositionY', 'lat', 'lon', 'speed']].to_dict(orient='records'),
        "bounds": {
            "minX": float(df_lap['WorldPositionX'].min()),
            "maxX": float(df_lap['WorldPositionX'].max()),
            "minY": float(df_lap['WorldPositionY'].min()),
            "maxY": float(df_lap['WorldPositionY'].max())
        }
    }

@app.get("/api/weather")
def get_weather():
    df = load_weather()
    if df.empty:
        return {}
    return df.iloc[0].to_dict()

@app.get("/api/sectors/{lap}")
def get_sector_analysis(lap: int, vehicle_number: Optional[int] = None):
    """Get sector-by-sector analysis with intermediate times"""
    try:
        df = pd.read_csv(SECTORS_PATH, sep=';')
        df_lap = df[df[' LAP_NUMBER'] == lap].copy()

        if vehicle_number:
            df_lap = df_lap[df_lap['NUMBER'] == vehicle_number]

        if df_lap.empty:
            raise HTTPException(status_code=404, detail=f"No sector data for lap {lap}")

        # Parse time strings to seconds
        def parse_time(time_str):
            if pd.isna(time_str):
                return None
            try:
                return pd.to_timedelta('00:' + str(time_str)).total_seconds()
            except:
                return None

        results = []
        for _, row in df_lap.iterrows():
            results.append({
                "vehicle_number": int(row['NUMBER']),
                "lap": int(row[' LAP_NUMBER']),
                "lap_time": str(row[' LAP_TIME']),
                "lap_time_seconds": parse_time(row[' LAP_TIME']),
                "sectors": {
                    "s1": {"time": str(row[' S1']), "seconds": float(row['S1_SECONDS']) if 'S1_SECONDS' in row and pd.notna(row['S1_SECONDS']) else None, "improvement": int(row[' S1_IMPROVEMENT'])},
                    "s2": {"time": str(row[' S2']), "seconds": float(row['S2_SECONDS']) if 'S2_SECONDS' in row and pd.notna(row['S2_SECONDS']) else None, "improvement": int(row[' S2_IMPROVEMENT'])},
                    "s3": {"time": str(row[' S3']), "seconds": float(row['S3_SECONDS']) if 'S3_SECONDS' in row and pd.notna(row['S3_SECONDS']) else None, "improvement": int(row[' S3_IMPROVEMENT'])}
                },
                "speed": {"average_kph": float(row[' KPH']), "top_speed": float(row['TOP_SPEED']) if pd.notna(row['TOP_SPEED']) else None},
                "intermediates": {
                    "im1a": float(row['IM1a_time']) if pd.notna(row.get('IM1a_time')) else None,
                    "im1": float(row['IM1_time']) if pd.notna(row.get('IM1_time')) else None,
                    "im2a": parse_time(row.get('IM2a_time')),
                    "im2": parse_time(row.get('IM2_time')),
                    "im3a": float(row['IM3a_time']) if pd.notna(row.get('IM3a_time')) else None
                }
            })

        return {"lap": lap, "vehicle_count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/sectors/compare")
def compare_sectors(lap1: int, lap2: int, vehicle_number: int):
    """Compare two laps sector-by-sector"""
    data1 = get_sector_analysis(lap1, vehicle_number)
    data2 = get_sector_analysis(lap2, vehicle_number)

    if not data1['data'] or not data2['data']:
        raise HTTPException(status_code=404, detail="Lap not found")

    lap1_data, lap2_data = data1['data'][0], data2['data'][0]

    return {
        "vehicle_number": vehicle_number,
        "comparison": {
            "lap_time_delta": lap1_data['lap_time_seconds'] - lap2_data['lap_time_seconds'],
            "sector_deltas": {
                "s1": (lap1_data['sectors']['s1']['seconds'] or 0) - (lap2_data['sectors']['s1']['seconds'] or 0),
                "s2": (lap1_data['sectors']['s2']['seconds'] or 0) - (lap2_data['sectors']['s2']['seconds'] or 0),
                "s3": (lap1_data['sectors']['s3']['seconds'] or 0) - (lap2_data['sectors']['s3']['seconds'] or 0)
            },
            "faster_lap": lap1 if lap1_data['lap_time_seconds'] < lap2_data['lap_time_seconds'] else lap2
        }
    }

@app.get("/api/lap_times")
def get_lap_times():
    df = load_lap_times()
    if df.empty:
        return []
    return df.to_dict(orient='records')

@app.get("/api/best_laps/{vehicle_number}")
def get_best_laps(vehicle_number: int):
    """Get top 10 best laps for a driver with detailed analysis"""
    try:
        df = pd.read_csv(BEST_LAPS_PATH, sep=';')
        driver_data = df[df['NUMBER'] == vehicle_number]

        if driver_data.empty:
            raise HTTPException(status_code=404, detail=f"Vehicle {vehicle_number} not found")

        row = driver_data.iloc[0]

        best_laps = []
        for i in range(1, 11):
            lap_time = row.get(f'BESTLAP_{i}')
            lap_num = row.get(f'BESTLAP_{i}_LAPNUM')

            if pd.notna(lap_time) and pd.notna(lap_num):
                best_laps.append({
                    "rank": i,
                    "lap_number": int(lap_num),
                    "lap_time": str(lap_time),
                    "lap_time_seconds": pd.to_timedelta('00:' + str(lap_time)).total_seconds() if ':' in str(lap_time) else float(lap_time)
                })

        return {
            "vehicle_number": vehicle_number,
            "vehicle": str(row['VEHICLE']),
            "class": str(row['CLASS']),
            "total_laps": int(row['TOTAL_DRIVER_LAPS']),
            "average_time": str(row['AVERAGE']),
            "best_laps": best_laps,
            "consistency_score": calculate_consistency(best_laps)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def calculate_consistency(laps):
    """Calculate driver consistency from lap times"""
    if len(laps) < 2:
        return 100.0
    times = [lap['lap_time_seconds'] for lap in laps if lap['lap_time_seconds']]
    if not times:
        return 0.0
    avg = sum(times) / len(times)
    variance = sum((t - avg) ** 2 for t in times) / len(times)
    std_dev = variance ** 0.5
    consistency = max(0, 100 - (std_dev / avg * 100))
    return round(consistency, 2)

@app.get("/api/perfect_lap")
def construct_perfect_lap():
    """Construct theoretical perfect lap from best sectors across all laps"""
    try:
        df = pd.read_csv(SECTORS_PATH, sep=';')

        # Find best sector times across all laps
        best_s1 = df.loc[df['S1_SECONDS'].idxmin()]
        best_s2 = df.loc[df['S2_SECONDS'].idxmin()]
        best_s3 = df.loc[df['S3_SECONDS'].idxmin()]

        perfect_time = best_s1['S1_SECONDS'] + best_s2['S2_SECONDS'] + best_s3['S3_SECONDS']

        return {
            "perfect_lap_time": round(perfect_time, 3),
            "best_sectors": {
                "s1": {
                    "time": float(best_s1['S1_SECONDS']),
                    "vehicle": int(best_s1['NUMBER']),
                    "lap": int(best_s1[' LAP_NUMBER'])
                },
                "s2": {
                    "time": float(best_s2['S2_SECONDS']),
                    "vehicle": int(best_s2['NUMBER']),
                    "lap": int(best_s2[' LAP_NUMBER'])
                },
                "s3": {
                    "time": float(best_s3['S3_SECONDS']),
                    "vehicle": int(best_s3['NUMBER']),
                    "lap": int(best_s3[' LAP_NUMBER'])
                }
            },
            "actual_best_lap": float(df[' LAP_TIME'].apply(lambda x: pd.to_timedelta('00:' + str(x)).total_seconds()).min()),
            "improvement_potential": round(float(df[' LAP_TIME'].apply(lambda x: pd.to_timedelta('00:' + str(x)).total_seconds()).min()) - perfect_time, 3)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/ml/validate")
def validate_ml_predictions():
    """Validate ML lap predictor against ground truth lap times"""
    try:
        # Load ground truth
        lap_times_df = pd.read_csv(LAP_TIMES_PATH)
        lap_times_df['lap_time_seconds'] = lap_times_df['value'] / 1000.0  # Convert ms to seconds

        # Load telemetry
        telemetry_df = load_telemetry()

        if ml_models['lap_predictor'] is None:
            return {"error": "ML model not loaded", "predictions": []}

        results = []
        for _, row in lap_times_df.head(10).iterrows():
            lap_num = int(row['lap'])
            actual_time = float(row['lap_time_seconds'])

            # Get telemetry for this lap
            lap_data = telemetry_df[telemetry_df['lap'] == lap_num]

            if not lap_data.empty:
                try:
                    predicted_time = ml_models['lap_predictor'].predict_from_telemetry(lap_data)
                    error = abs(predicted_time - actual_time)

                    results.append({
                        "lap": lap_num,
                        "actual_time": round(actual_time, 3),
                        "predicted_time": round(float(predicted_time), 3),
                        "error_seconds": round(error, 3),
                        "error_percentage": round((error / actual_time) * 100, 2)
                    })
                except:
                    pass

        # Calculate overall metrics
        if results:
            errors = [r['error_seconds'] for r in results]
            mae = sum(errors) / len(errors)
            rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5

            return {
                "validation_count": len(results),
                "mae": round(mae, 3),
                "rmse": round(rmse, 3),
                "predictions": results
            }
        else:
            return {"error": "No predictions made", "predictions": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

class ChatRequest(BaseModel):
    message: str
    lap: Optional[int] = None

# ============================================
# ANOMALY DETECTION
# ============================================
def detect_anomalies(df_main, df_ref, speed_threshold=15.0):
    """Detect anomalies where main driver is significantly slower than reference."""
    if df_main.empty or df_ref.empty:
        return []

    # Interpolate main speed to reference distance
    common_distance = df_ref['distance'].values
    main_speed_interp = np.interp(common_distance, df_main['distance'].values, df_main['speed'].values)

    # Calculate delta
    speed_delta = df_ref['speed'].values - main_speed_interp

    # Find anomalies
    anomalies = []
    for i, delta in enumerate(speed_delta):
        if delta > speed_threshold:
            anomalies.append({
                "distance": float(common_distance[i]),
                "ref_speed": float(df_ref['speed'].iloc[i]),
                "user_speed": float(main_speed_interp[i]),
                "speed_delta": float(delta),
                "x": float(df_ref['WorldPositionX'].iloc[i]) if 'WorldPositionX' in df_ref.columns else 0,
                "y": float(df_ref['WorldPositionY'].iloc[i]) if 'WorldPositionY' in df_ref.columns else 0,
                "lat": float(df_ref['lat'].iloc[i]) if 'lat' in df_ref.columns else 0,
                "lon": float(df_ref['lon'].iloc[i]) if 'lon' in df_ref.columns else 0,
            })

    return anomalies

@app.get("/api/best_lap")
def get_best_lap():
    """Find the best lap (fastest) from lap times or telemetry."""
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    # Calculate lap times from telemetry
    laps = df['lap'].unique()
    lap_times = []

    for lap in laps:
        df_lap = df[df['lap'] == lap]
        if len(df_lap) > 10:
            lap_time = (df_lap['timestamp'].max() - df_lap['timestamp'].min()).total_seconds()
            lap_times.append({"lap": int(lap), "time": lap_time})

    if not lap_times:
        raise HTTPException(status_code=404, detail="No valid laps")

    # Sort by time
    lap_times.sort(key=lambda x: x['time'])
    best = lap_times[0]

    return {
        "best_lap": best['lap'],
        "best_time": best['time'],
        "all_lap_times": lap_times
    }

@app.get("/api/anomalies/{lap}")
def get_anomalies(lap: int, ref_lap: Optional[int] = None, threshold: float = 15.0, use_ml: bool = True):
    """
    Detect anomalies using ML Isolation Forest or reference lap comparison.
    ML model detects unusual driving patterns (sudden braking, erratic steering, etc.)
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_user = df[df['lap'] == lap].copy()
    if df_user.empty:
        raise HTTPException(status_code=404, detail="User lap not found")
    df_user['distance'] = df_user['distance'] - df_user['distance'].iloc[0]

    # Try ML-based anomaly detection first
    if use_ml and ml_models['anomaly_detector'] is not None:
        try:
            ml_report = ml_models['anomaly_detector'].get_anomaly_report(df_user)

            return {
                "user_lap": lap,
                "detection_method": "ML_IsolationForest",
                "anomaly_count": ml_report['anomaly_count'],
                "anomaly_percentage": round(ml_report['anomaly_percentage'], 2),
                "total_points": ml_report['total_points'],
                "anomalies": ml_report['anomalies'][:20]  # Top 20 anomalies
            }
        except Exception as e:
            print(f"ML anomaly detection failed, using fallback: {e}")

    # Fallback: Reference lap comparison
    if ref_lap is None:
        best_lap_data = get_best_lap()
        ref_lap = best_lap_data['best_lap']

    df_ref = df[df['lap'] == ref_lap].copy()
    if df_ref.empty:
        raise HTTPException(status_code=404, detail="Reference lap not found")
    df_ref['distance'] = df_ref['distance'] - df_ref['distance'].iloc[0]

    anomalies = detect_anomalies(df_user, df_ref, threshold)

    explanations = []
    for a in sorted(anomalies, key=lambda x: x['speed_delta'], reverse=True)[:10]:
        if a['speed_delta'] > 30:
            reason = "Critical speed loss - possible missed apex or heavy braking"
        elif a['speed_delta'] > 20:
            reason = "Significant speed loss - check braking point"
        else:
            reason = "Minor speed loss - optimize racing line"
        explanations.append({**a, "reason": reason, "type": "speed_comparison"})

    return {
        "user_lap": lap,
        "ref_lap": ref_lap,
        "detection_method": "reference_comparison",
        "threshold": threshold,
        "anomaly_count": len(anomalies),
        "anomalies": explanations
    }

# ============================================
# LAP COMPARISON
# ============================================
@app.get("/api/compare/{lap1}/{lap2}")
def compare_laps(lap1: int, lap2: int, points: int = 200):
    """Compare two laps side by side."""
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    # Get lap 1
    df_lap1 = df[df['lap'] == lap1].copy()
    if df_lap1.empty:
        raise HTTPException(status_code=404, detail=f"Lap {lap1} not found")
    df_lap1['distance'] = df_lap1['distance'] - df_lap1['distance'].iloc[0]

    # Get lap 2
    df_lap2 = df[df['lap'] == lap2].copy()
    if df_lap2.empty:
        raise HTTPException(status_code=404, detail=f"Lap {lap2} not found")
    df_lap2['distance'] = df_lap2['distance'] - df_lap2['distance'].iloc[0]

    # Sample both laps
    def sample_lap(df_lap, n):
        if len(df_lap) > n:
            indices = np.linspace(0, len(df_lap)-1, n, dtype=int)
            return df_lap.iloc[indices]
        return df_lap

    df_lap1 = sample_lap(df_lap1, points)
    df_lap2 = sample_lap(df_lap2, points)

    # Create common distance axis
    max_dist = min(df_lap1['distance'].max(), df_lap2['distance'].max())
    common_dist = np.linspace(0, max_dist, points)

    # Interpolate both laps to common distance
    def interp_lap(df_lap, dist):
        result = {'distance': dist.tolist()}
        for col in ['speed', 'nmot', 'ath', 'pbrake_f', 'Steering_Angle']:
            if col in df_lap.columns:
                result[col] = np.interp(dist, df_lap['distance'].values, df_lap[col].values).tolist()
        return result

    lap1_data = interp_lap(df_lap1, common_dist)
    lap2_data = interp_lap(df_lap2, common_dist)

    # Calculate deltas
    speed_delta = [lap1_data['speed'][i] - lap2_data['speed'][i] for i in range(len(common_dist))]
    cumulative_delta = np.cumsum([d / 3.6 * 0.01 for d in speed_delta]).tolist()  # Approximate time delta

    # Stats
    lap1_time = (df[df['lap'] == lap1]['timestamp'].max() - df[df['lap'] == lap1]['timestamp'].min()).total_seconds()
    lap2_time = (df[df['lap'] == lap2]['timestamp'].max() - df[df['lap'] == lap2]['timestamp'].min()).total_seconds()

    return {
        "lap1": {"number": lap1, "time": lap1_time, "data": lap1_data},
        "lap2": {"number": lap2, "time": lap2_time, "data": lap2_data},
        "delta": {
            "distance": common_dist.tolist(),
            "speed_delta": speed_delta,
            "cumulative_time_delta": cumulative_delta
        },
        "time_difference": lap1_time - lap2_time
    }

# ============================================
# SUGGESTIONS
# ============================================
@app.get("/api/suggestions/{lap}")
def get_suggestions(lap: int):
    """Generate improvement suggestions based on anomaly analysis."""
    try:
        # Load data
        df = load_telemetry()
        if df.empty:
            return {"suggestions": []}

        # Get user lap
        df_user = df[df['lap'] == lap].copy()
        if df_user.empty:
            return {"suggestions": []}
        df_user['distance'] = df_user['distance'] - df_user['distance'].iloc[0]

        # Get best lap as reference
        best_lap_data = get_best_lap()
        ref_lap = best_lap_data['best_lap']

        df_ref = df[df['lap'] == ref_lap].copy()
        if df_ref.empty:
            return {"suggestions": []}
        df_ref['distance'] = df_ref['distance'] - df_ref['distance'].iloc[0]

        # Detect anomalies
        anomalies = detect_anomalies(df_user, df_ref, speed_threshold=15.0)
    except Exception as e:
        print(f"Error in get_suggestions: {e}")
        anomalies = []

    suggestions = []

    if not anomalies:
        suggestions.append({
            "type": "general",
            "title": "Good Performance",
            "description": "No significant anomalies detected. Focus on consistency.",
            "priority": "low"
        })
    else:
        # Group anomalies by distance zones
        zones = {}
        for a in anomalies:
            zone = int(a['distance'] // 500) * 500  # 500m zones
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(a)

        for zone, zone_anomalies in sorted(zones.items()):
            avg_delta = sum(a['speed_delta'] for a in zone_anomalies) / len(zone_anomalies)

            if avg_delta > 25:
                priority = "high"
                title = f"Critical Zone: {zone}m - {zone+500}m"
                desc = f"Average speed loss of {avg_delta:.1f} km/h. Check braking point and apex."
            elif avg_delta > 15:
                priority = "medium"
                title = f"Improvement Zone: {zone}m - {zone+500}m"
                desc = f"Speed loss of {avg_delta:.1f} km/h. Optimize racing line."
            else:
                continue

            suggestions.append({
                "type": "zone",
                "title": title,
                "description": desc,
                "priority": priority,
                "distance_start": zone,
                "distance_end": zone + 500,
                "speed_delta": avg_delta
            })

    # Add general suggestions
    df = load_telemetry()
    if not df.empty:
        df_lap = df[df['lap'] == lap]
        if not df_lap.empty:
            avg_throttle = df_lap['ath'].mean()
            max_brake = df_lap['pbrake_f'].max()

            if avg_throttle < 60:
                suggestions.append({
                    "type": "throttle",
                    "title": "Throttle Application",
                    "description": f"Average throttle is {avg_throttle:.1f}%. Consider more aggressive acceleration.",
                    "priority": "medium"
                })

            if max_brake > 80:
                suggestions.append({
                    "type": "braking",
                    "title": "Braking Intensity",
                    "description": f"Max brake pressure is {max_brake:.1f}. Try earlier, lighter braking.",
                    "priority": "low"
                })

    return {
        "lap": lap,
        "suggestion_count": len(suggestions),
        "suggestions": suggestions
    }

# ============================================
# REPORT GENERATION
# ============================================
@app.get("/api/report/{lap}")
def generate_report(lap: int, format: str = "json"):
    """Generate a comprehensive lap analysis report."""
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    # Gather all data
    try:
        anomaly_data = get_anomalies(lap)
    except:
        anomaly_data = {"anomalies": [], "anomaly_count": 0}

    try:
        suggestion_data = get_suggestions(lap)
    except:
        suggestion_data = {"suggestions": []}

    try:
        best_lap_data = get_best_lap()
    except:
        best_lap_data = {"best_lap": None}

    weather = load_weather()
    weather_data = weather.iloc[0].to_dict() if not weather.empty else {}

    # Calculate lap stats
    lap_time = (df_lap['timestamp'].max() - df_lap['timestamp'].min()).total_seconds()

    report = {
        "report_type": "Lap Analysis Report",
        "lap_number": lap,
        "lap_time": lap_time,
        "best_lap": best_lap_data.get('best_lap'),
        "best_lap_time": best_lap_data.get('best_time'),
        "statistics": {
            "max_speed": float(df_lap['speed'].max()),
            "avg_speed": float(df_lap['speed'].mean()),
            "min_speed": float(df_lap['speed'].min()),
            "max_rpm": float(df_lap['nmot'].max()) if 'nmot' in df_lap.columns else 0,
            "avg_rpm": float(df_lap['nmot'].mean()) if 'nmot' in df_lap.columns else 0,
            "avg_throttle": float(df_lap['ath'].mean()) if 'ath' in df_lap.columns else 0,
            "max_brake": float(df_lap['pbrake_f'].max()) if 'pbrake_f' in df_lap.columns else 0,
            "distance": float(df_lap['distance'].max() - df_lap['distance'].min()),
        },
        "anomalies": {
            "count": anomaly_data.get('anomaly_count', 0),
            "details": anomaly_data.get('anomalies', [])[:10]
        },
        "suggestions": suggestion_data.get('suggestions', []),
        "weather": weather_data,
        "summary": ""
    }

    # Generate AI summary if available
    if groq_client:
        try:
            summary_prompt = f"""Generate a brief race engineer summary for this lap:
- Lap Time: {lap_time:.2f}s (Best: {best_lap_data.get('best_time', 'N/A')})
- Max Speed: {report['statistics']['max_speed']:.1f} km/h
- Anomalies: {report['anomalies']['count']} detected
- Top suggestion: {report['suggestions'][0]['description'] if report['suggestions'] else 'None'}

Keep it under 100 words, professional tone."""

            response = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are GR-Pilot, a professional race engineer."},
                    {"role": "user", "content": summary_prompt}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=150,
            )
            report['summary'] = response.choices[0].message.content
        except:
            report['summary'] = f"Lap {lap} completed in {lap_time:.2f}s with {report['anomalies']['count']} anomalies detected."
    else:
        report['summary'] = f"Lap {lap} completed in {lap_time:.2f}s with {report['anomalies']['count']} anomalies detected."

    return report

# ============================================
# DRIVER DNA - ML-Powered Sürüş Karakteri Analizi
# ============================================
@app.get("/api/driver_dna/{lap}")
def get_driver_dna(lap: int):
    """
    Analyze driver's unique driving signature using ML clustering.
    Uses trained K-Means model to classify driving style.
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # Try ML model first
    if ml_models['driver_clusterer'] is not None:
        try:
            dna_result = ml_models['driver_clusterer'].get_driver_dna(df_lap)

            # Build pattern data for visualization
            pattern_data = []
            step = max(1, len(df_lap) // 50)
            for i in range(0, len(df_lap), step):
                point = df_lap.iloc[i]
                pattern_data.append({
                    "distance": float(point['distance']),
                    "throttle": float(point['ath']) if 'ath' in point else 0,
                    "brake": float(point['pbrake_f']) if 'pbrake_f' in point else 0,
                    "steering": float(point['Steering_Angle']) if 'Steering_Angle' in point else 0
                })

            return {
                "lap": lap,
                "model_type": "ML_KMeans_Clustering",
                "driver_type": dna_result['style_name'],
                "driver_description": dna_result['style_description'],
                "dna_scores": dna_result['dna_scores'],
                "cluster_id": dna_result['cluster_id'],
                "recommendations": dna_result['recommendations'],
                "metrics": dna_result['raw_metrics'],
                "pattern_data": pattern_data
            }
        except Exception as e:
            print(f"ML model error, falling back: {e}")

    # Fallback to rule-based analysis
    throttle_aggressiveness = df_lap['ath'].std() if 'ath' in df_lap.columns else 0
    throttle_avg = df_lap['ath'].mean() if 'ath' in df_lap.columns else 0
    full_throttle_pct = (df_lap['ath'] > 90).sum() / len(df_lap) * 100 if 'ath' in df_lap.columns else 0
    brake_intensity = df_lap['pbrake_f'].mean() if 'pbrake_f' in df_lap.columns else 0
    brake_max = df_lap['pbrake_f'].max() if 'pbrake_f' in df_lap.columns else 0
    hard_brake_pct = (df_lap['pbrake_f'] > 50).sum() / len(df_lap) * 100 if 'pbrake_f' in df_lap.columns else 0
    steering_smoothness = 100 - min(df_lap['Steering_Angle'].diff().abs().mean(), 100) if 'Steering_Angle' in df_lap.columns else 50
    steering_corrections = (df_lap['Steering_Angle'].diff().abs() > 5).sum() if 'Steering_Angle' in df_lap.columns else 0
    speed_consistency = 100 - min(df_lap['speed'].std() / df_lap['speed'].mean() * 100, 100) if 'speed' in df_lap.columns else 50

    aggression_score = min((throttle_aggressiveness * 2 + hard_brake_pct) / 2, 100)
    smoothness_score = min((steering_smoothness + speed_consistency) / 2, 100)
    consistency_score = min(100 - (steering_corrections / len(df_lap) * 1000), 100)

    if aggression_score > 70 and smoothness_score < 50:
        driver_type, driver_desc = "Aggressive Attacker", "High risk, high reward style."
    elif smoothness_score > 70 and aggression_score < 40:
        driver_type, driver_desc = "Smooth Operator", "Consistent and precise."
    elif aggression_score > 50 and smoothness_score > 50:
        driver_type, driver_desc = "Balanced Racer", "Good mix of speed and consistency."
    else:
        driver_type, driver_desc = "Conservative Driver", "Safe approach."

    pattern_data = []
    step = max(1, len(df_lap) // 50)
    for i in range(0, len(df_lap), step):
        point = df_lap.iloc[i]
        pattern_data.append({
            "distance": float(point['distance']),
            "throttle": float(point['ath']) if 'ath' in point else 0,
            "brake": float(point['pbrake_f']) if 'pbrake_f' in point else 0,
            "steering": float(point['Steering_Angle']) if 'Steering_Angle' in point else 0
        })

    return {
        "lap": lap,
        "model_type": "rule_based_fallback",
        "driver_type": driver_type,
        "driver_description": driver_desc,
        "dna_scores": {
            "aggression": round(aggression_score, 1),
            "smoothness": round(smoothness_score, 1),
            "consistency": round(consistency_score, 1)
        },
        "metrics": {
            "throttle_avg": round(throttle_avg, 1),
            "full_throttle_pct": round(full_throttle_pct, 1),
            "brake_max": round(brake_max, 1),
            "hard_brake_pct": round(hard_brake_pct, 1),
            "steering_corrections": int(steering_corrections)
        },
        "pattern_data": pattern_data
    }

# ============================================
# GRIP INDEX - Weather + Telemetry Fusion
# ============================================
@app.get("/api/grip_index/{lap}")
def get_grip_index(lap: int):
    """
    Calculate grip index by combining weather data with telemetry.
    Higher index = better grip conditions.
    """
    df = load_telemetry()
    weather = load_weather()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # Real weather data
    if not weather.empty:
        track_temp = float(weather.iloc[0].get('TRACK_TEMP', 35))
        ambient_temp = float(weather.iloc[0].get('AIR_TEMP', 25))
        humidity = float(weather.iloc[0].get('HUMIDITY', 50))
    else:
        track_temp, ambient_temp, humidity = 35, 25, 50

    if not weather.empty:
        w = weather.iloc[0]
        track_temp = float(w.get('track_temp', w.get('TrackTemp', 35)))
        ambient_temp = float(w.get('ambient_temp', w.get('AmbientTemp', 25)))
        humidity = float(w.get('humidity', w.get('Humidity', 50)))

    # Temperature impact on grip (optimal around 30-45°C for track)
    temp_factor = 100 - abs(track_temp - 37.5) * 2
    temp_factor = max(0, min(100, temp_factor))

    # Humidity impact (lower is better for grip)
    humidity_factor = 100 - humidity * 0.5

    # Base grip from weather
    weather_grip = (temp_factor * 0.6 + humidity_factor * 0.4)

    # Calculate grip index along the track
    grip_data = []
    step = max(1, len(df_lap) // 100)

    for i in range(0, len(df_lap), step):
        point = df_lap.iloc[i]

        # Lateral G estimation from steering and speed
        speed = point['speed'] if 'speed' in point else 0
        steering = abs(point['Steering_Angle']) if 'Steering_Angle' in point else 0

        # Higher speed + higher steering = more lateral load = grip test
        lateral_load = (speed / 200) * (steering / 100) * 100

        # Brake pressure impact
        brake = point['pbrake_f'] if 'pbrake_f' in point else 0
        longitudinal_load = brake * 1.5

        # Combined grip demand
        grip_demand = min(np.sqrt(lateral_load**2 + longitudinal_load**2), 100)

        # Estimated grip available (weather base - tire wear simulation)
        distance_factor = 1 - (point['distance'] / (df_lap['distance'].max() + 1)) * 0.1
        grip_available = weather_grip * distance_factor

        # Grip margin (positive = safe, negative = sliding)
        grip_margin = grip_available - grip_demand

        grip_data.append({
            "distance": float(point['distance']),
            "grip_demand": round(grip_demand, 1),
            "grip_available": round(grip_available, 1),
            "grip_margin": round(grip_margin, 1),
            "lateral_load": round(lateral_load, 1),
            "x": float(point['WorldPositionX']) if 'WorldPositionX' in point else 0,
            "y": float(point['WorldPositionY']) if 'WorldPositionY' in point else 0
        })

    # Find critical zones (low grip margin)
    critical_zones = [g for g in grip_data if g['grip_margin'] < 10]

    return {
        "lap": lap,
        "overall_grip_index": round(weather_grip, 1),
        "weather_factors": {
            "track_temp": track_temp,
            "ambient_temp": ambient_temp,
            "humidity": humidity,
            "temp_factor": round(temp_factor, 1),
            "humidity_factor": round(humidity_factor, 1)
        },
        "grip_data": grip_data,
        "critical_zones_count": len(critical_zones),
        "critical_zones": critical_zones[:10],
        "recommendation": "Good grip conditions" if weather_grip > 70 else "Caution: Reduced grip" if weather_grip > 50 else "Warning: Low grip conditions"
    }

# ============================================
# SECTOR ANALYSIS - Time Gain/Loss (REAL DATA)
# ============================================
@app.get("/api/sectors/{lap}")
def get_sector_analysis(lap: int, driver_number: int = 1):
    """
    Get real sector times from race data.
    Uses actual S1, S2, S3 times from the timing system.
    """
    sectors_df = load_sectors()
    df = load_telemetry()

    # Try to use real sector data first
    if not sectors_df.empty:
        # Filter by driver and lap
        driver_data = sectors_df[sectors_df[' DRIVER_NUMBER'] == driver_number]
        lap_data = driver_data[driver_data[' LAP_NUMBER'] == lap]

        if not lap_data.empty:
            row = lap_data.iloc[0]

            # Get best sectors from all laps for this driver
            best_s1 = driver_data[' S1_SECONDS'].min()
            best_s2 = driver_data[' S2_SECONDS'].min()
            best_s3 = driver_data[' S3_SECONDS'].min()

            s1_time = float(row[' S1_SECONDS'])
            s2_time = float(row[' S2_SECONDS'])
            s3_time = float(row[' S3_SECONDS'])

            sectors = [
                {
                    "sector": 1,
                    "time": round(s1_time, 3),
                    "best_time": round(best_s1, 3),
                    "time_delta": round(s1_time - best_s1, 3),
                    "status": "faster" if s1_time <= best_s1 else "slower",
                    "color": "#22c55e" if s1_time <= best_s1 + 0.1 else "#ef4444",
                    "top_speed": float(row.get(' TOP_SPEED', 0)) if ' TOP_SPEED' in row else 0
                },
                {
                    "sector": 2,
                    "time": round(s2_time, 3),
                    "best_time": round(best_s2, 3),
                    "time_delta": round(s2_time - best_s2, 3),
                    "status": "faster" if s2_time <= best_s2 else "slower",
                    "color": "#22c55e" if s2_time <= best_s2 + 0.1 else "#ef4444"
                },
                {
                    "sector": 3,
                    "time": round(s3_time, 3),
                    "best_time": round(best_s3, 3),
                    "time_delta": round(s3_time - best_s3, 3),
                    "status": "faster" if s3_time <= best_s3 else "slower",
                    "color": "#22c55e" if s3_time <= best_s3 + 0.1 else "#ef4444"
                }
            ]

            total_time = s1_time + s2_time + s3_time
            theoretical_best = best_s1 + best_s2 + best_s3

            return {
                "lap": lap,
                "driver_number": driver_number,
                "data_source": "official_timing",
                "sectors": sectors,
                "total_time": round(total_time, 3),
                "theoretical_best": round(theoretical_best, 3),
                "potential_gain": round(total_time - theoretical_best, 3),
                "lap_time_official": str(row.get(' LAP_TIME', '')),
                "top_speed": float(row.get(' TOP_SPEED', 0)) if ' TOP_SPEED' in row else 0,
                "class": str(row.get(' CLASS', '')).strip() if ' CLASS' in row else ""
            }

    # Fallback to telemetry-based calculation
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]
    max_distance = df_lap['distance'].max()

    # 3 sectors like real racing
    num_sectors = 3
    sector_length = max_distance / num_sectors
    sectors = []

    for i in range(num_sectors):
        start_dist = i * sector_length
        end_dist = (i + 1) * sector_length
        sector_data = df_lap[(df_lap['distance'] >= start_dist) & (df_lap['distance'] < end_dist)]

        if len(sector_data) >= 2:
            sector_time = (sector_data['timestamp'].max() - sector_data['timestamp'].min()).total_seconds()
            sectors.append({
                "sector": i + 1,
                "time": round(sector_time, 3),
                "best_time": round(sector_time, 3),
                "time_delta": 0,
                "avg_speed": round(sector_data['speed'].mean(), 1),
                "max_speed": round(sector_data['speed'].max(), 1),
                "status": "equal",
                "color": "#fbbf24"
            })

    total_time = sum(s['time'] for s in sectors)

    return {
        "lap": lap,
        "data_source": "telemetry",
        "sectors": sectors,
        "total_time": round(total_time, 3),
        "theoretical_best": round(total_time, 3),
        "potential_gain": 0
    }

# ============================================
# RISK HEATMAP - Spin/Lock-up Risk
# ============================================
@app.get("/api/risk_heatmap/{lap}")
def get_risk_heatmap(lap: int):
    """
    Calculate risk zones for spin, lock-up, and other incidents.
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    risk_data = []
    step = max(1, len(df_lap) // 100)

    for i in range(0, len(df_lap), step):
        point = df_lap.iloc[i]

        speed = point['speed'] if 'speed' in point else 0
        throttle = point['ath'] if 'ath' in point else 0
        brake = point['pbrake_f'] if 'pbrake_f' in point else 0
        steering = abs(point['Steering_Angle']) if 'Steering_Angle' in point else 0

        # Lock-up risk: high brake + high speed + steering input
        lockup_risk = min((brake / 100) * (speed / 200) * (1 + steering / 200) * 100, 100)

        # Spin risk: high throttle + high steering + lower speed (corner exit)
        spin_risk = min((throttle / 100) * (steering / 100) * (1 - speed / 300) * 150, 100)

        # Oversteer risk: sudden steering changes + speed
        steering_rate = 0
        if i > 0:
            prev_steering = df_lap.iloc[i-step]['Steering_Angle'] if 'Steering_Angle' in df_lap.columns else 0
            steering_rate = abs(steering - abs(prev_steering))
        oversteer_risk = min(steering_rate * (speed / 150), 100)

        # Combined risk
        total_risk = max(lockup_risk, spin_risk, oversteer_risk)

        # Determine risk type
        if total_risk == lockup_risk and lockup_risk > 30:
            risk_type = "lock-up"
        elif total_risk == spin_risk and spin_risk > 30:
            risk_type = "spin"
        elif total_risk == oversteer_risk and oversteer_risk > 30:
            risk_type = "oversteer"
        else:
            risk_type = "low"

        risk_data.append({
            "distance": float(point['distance']),
            "x": float(point['WorldPositionX']) if 'WorldPositionX' in point else 0,
            "y": float(point['WorldPositionY']) if 'WorldPositionY' in point else 0,
            "lockup_risk": round(lockup_risk, 1),
            "spin_risk": round(spin_risk, 1),
            "oversteer_risk": round(oversteer_risk, 1),
            "total_risk": round(total_risk, 1),
            "risk_type": risk_type,
            "speed": round(speed, 1),
            "brake": round(brake, 1),
            "throttle": round(throttle, 1)
        })

    # Find high risk zones
    high_risk_zones = [r for r in risk_data if r['total_risk'] > 50]
    critical_zones = [r for r in risk_data if r['total_risk'] > 75]

    # Risk summary
    avg_risk = sum(r['total_risk'] for r in risk_data) / len(risk_data) if risk_data else 0
    max_risk = max(r['total_risk'] for r in risk_data) if risk_data else 0

    return {
        "lap": lap,
        "risk_summary": {
            "average_risk": round(avg_risk, 1),
            "max_risk": round(max_risk, 1),
            "high_risk_zones": len(high_risk_zones),
            "critical_zones": len(critical_zones)
        },
        "risk_data": risk_data,
        "high_risk_points": high_risk_zones[:15],
        "recommendation": "Safe driving" if avg_risk < 30 else "Moderate risk - stay focused" if avg_risk < 50 else "High risk - reduce aggression"
    }

# ============================================
# TIRE STRESS SCORE
# ============================================
@app.get("/api/tire_stress/{lap}")
def get_tire_stress(lap: int):
    """
    Estimate tire stress/wear based on driving inputs and track position.
    """
    df = load_telemetry()
    weather = load_weather()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # Real weather impact on tire wear
    if not weather.empty:
        track_temp = float(weather.iloc[0].get('TRACK_TEMP', 35))
        ambient_temp = float(weather.iloc[0].get('AIR_TEMP', 25))
    else:
        track_temp, ambient_temp = 35, 25

    # Temperature wear multiplier (higher temp = more wear)
    temp_multiplier = 1 + (track_temp - 30) * 0.02

    tire_data = []
    cumulative_stress = {"FL": 0, "FR": 0, "RL": 0, "RR": 0}
    step = max(1, len(df_lap) // 100)

    for i in range(0, len(df_lap), step):
        point = df_lap.iloc[i]

        speed = point['speed'] if 'speed' in point else 0
        throttle = point['ath'] if 'ath' in point else 0
        brake = point['pbrake_f'] if 'pbrake_f' in point else 0
        steering = point['Steering_Angle'] if 'Steering_Angle' in point else 0

        # Lateral stress from cornering
        lateral_stress = abs(steering) * (speed / 150) * 0.5

        # Longitudinal stress from acceleration/braking
        accel_stress = throttle * (speed / 200) * 0.3
        brake_stress = brake * 0.8

        # Per-tire stress calculation
        if steering > 0:  # Right turn - more stress on left tires
            fl_stress = lateral_stress * 1.2 + brake_stress * 0.6
            fr_stress = lateral_stress * 0.8 + brake_stress * 0.6
            rl_stress = lateral_stress * 1.0 + accel_stress * 0.6
            rr_stress = lateral_stress * 0.6 + accel_stress * 0.6
        else:  # Left turn - more stress on right tires
            fl_stress = lateral_stress * 0.8 + brake_stress * 0.6
            fr_stress = lateral_stress * 1.2 + brake_stress * 0.6
            rl_stress = lateral_stress * 0.6 + accel_stress * 0.6
            rr_stress = lateral_stress * 1.0 + accel_stress * 0.6

        # Apply temperature multiplier
        fl_stress *= temp_multiplier
        fr_stress *= temp_multiplier
        rl_stress *= temp_multiplier
        rr_stress *= temp_multiplier

        # Cumulative stress (simulated wear)
        cumulative_stress["FL"] += fl_stress * 0.01
        cumulative_stress["FR"] += fr_stress * 0.01
        cumulative_stress["RL"] += rl_stress * 0.01
        cumulative_stress["RR"] += rr_stress * 0.01

        tire_data.append({
            "distance": float(point['distance']),
            "instant_stress": {
                "FL": round(fl_stress, 1),
                "FR": round(fr_stress, 1),
                "RL": round(rl_stress, 1),
                "RR": round(rr_stress, 1)
            },
            "cumulative_wear": {
                "FL": round(cumulative_stress["FL"], 2),
                "FR": round(cumulative_stress["FR"], 2),
                "RL": round(cumulative_stress["RL"], 2),
                "RR": round(cumulative_stress["RR"], 2)
            }
        })

    # Final tire condition estimate (100 = new, 0 = worn out)
    max_wear = max(cumulative_stress.values())
    tire_condition = {
        "FL": round(max(0, 100 - cumulative_stress["FL"]), 1),
        "FR": round(max(0, 100 - cumulative_stress["FR"]), 1),
        "RL": round(max(0, 100 - cumulative_stress["RL"]), 1),
        "RR": round(max(0, 100 - cumulative_stress["RR"]), 1)
    }

    # Most stressed tire
    most_stressed = max(cumulative_stress, key=cumulative_stress.get)

    # Pit recommendation
    avg_condition = sum(tire_condition.values()) / 4
    if avg_condition < 30:
        pit_recommendation = "Pit NOW - Critical tire wear"
    elif avg_condition < 50:
        pit_recommendation = "Consider pitting soon"
    elif avg_condition < 70:
        pit_recommendation = "Tires holding up - monitor closely"
    else:
        pit_recommendation = "Tires in good condition"

    return {
        "lap": lap,
        "track_temp": track_temp,
        "temp_multiplier": round(temp_multiplier, 2),
        "tire_condition": tire_condition,
        "cumulative_stress": {k: round(v, 2) for k, v in cumulative_stress.items()},
        "most_stressed_tire": most_stressed,
        "average_condition": round(avg_condition, 1),
        "pit_recommendation": pit_recommendation,
        "tire_data": tire_data[::2]  # Every other point to reduce data
    }

# ============================================
# LAP TIME PREDICTION - ML XGBoost
# ============================================
@app.get("/api/predict_laptime/{lap}")
def predict_lap_time(lap: int):
    """
    Predict lap time using trained XGBoost model.
    Also provides feature importance for improvement suggestions.
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # Calculate actual lap time
    actual_time = (df_lap['timestamp'].max() - df_lap['timestamp'].min()).total_seconds()

    # Try ML prediction
    if ml_models['lap_predictor'] is not None:
        try:
            predicted_time = ml_models['lap_predictor'].predict_from_telemetry(df_lap)
            suggestions = ml_models['lap_predictor'].get_improvement_suggestions(df_lap)
            feature_importance = dict(list(ml_models['lap_predictor'].feature_importance.items())[:10])

            return {
                "lap": lap,
                "prediction_method": "ML_XGBoost",
                "actual_time": round(actual_time, 3),
                "predicted_time": round(predicted_time, 3),
                "prediction_error": round(abs(actual_time - predicted_time), 3),
                "feature_importance": feature_importance,
                "improvement_suggestions": suggestions
            }
        except Exception as e:
            print(f"ML prediction failed: {e}")

    # Fallback - return actual time only
    return {
        "lap": lap,
        "prediction_method": "not_available",
        "actual_time": round(actual_time, 3),
        "predicted_time": None,
        "message": "ML model not trained. Run train_models.py first."
    }

# ============================================
# COMPOSITE PERFORMANCE INDEX (CPI)
# ============================================
@app.get("/api/cpi/{lap}")
def get_composite_performance_index(lap: int):
    """
    Calculate Composite Performance Index (CPI) - Toyota's ultimate performance metric.
    Combines multiple telemetry channels into a single performance score (0-100).

    CPI Formula:
    - Speed Score (30%): How close to optimal speed
    - Brake Efficiency (20%): Smooth, late braking
    - Throttle Smoothness (15%): Progressive application
    - Tire Stress (15%): Minimizing tire degradation
    - Turn Entry Accuracy (10%): Optimal corner entry
    - Sector Consistency (10%): Lap-to-lap variation
    """
    df = load_telemetry()
    weather = load_weather()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]

    # 1. SPEED SCORE (30%) - Compare to theoretical maximum
    max_possible_speed = 280  # km/h for GR Cup
    avg_speed = df_lap['speed'].mean()
    speed_efficiency = (avg_speed / max_possible_speed) * 100
    speed_score = min(speed_efficiency * 1.2, 100)  # Boost for high speeds

    # 2. BRAKE EFFICIENCY (20%) - Late braking, smooth release
    brake_data = df_lap['pbrake_f'] if 'pbrake_f' in df_lap.columns else pd.Series([0]*len(df_lap))
    brake_events = (brake_data > 30).sum()
    total_points = len(df_lap)
    brake_time_pct = (brake_events / total_points) * 100

    # Lower brake time = better (optimal ~15-20%)
    if brake_time_pct < 10:
        brake_efficiency_score = 60  # Too little braking - missing apexes
    elif brake_time_pct < 20:
        brake_efficiency_score = 100  # Optimal
    elif brake_time_pct < 30:
        brake_efficiency_score = 80
    else:
        brake_efficiency_score = 50  # Over-braking

    # Brake smoothness
    brake_smoothness = 100 - min(brake_data.diff().abs().mean() * 2, 50)
    brake_score = (brake_efficiency_score * 0.6 + brake_smoothness * 0.4)

    # 3. THROTTLE SMOOTHNESS (15%) - Progressive application
    throttle_data = df_lap['ath'] if 'ath' in df_lap.columns else pd.Series([0]*len(df_lap))
    throttle_variance = throttle_data.std()
    throttle_avg = throttle_data.mean()

    # Penalize erratic throttle
    throttle_smoothness = 100 - min(throttle_variance, 40)
    # Reward high average throttle
    throttle_usage = min((throttle_avg / 80) * 100, 100)
    throttle_score = (throttle_smoothness * 0.5 + throttle_usage * 0.5)

    # 4. TIRE STRESS (15%) - Minimize wear
    steering_data = df_lap['Steering_Angle'] if 'Steering_Angle' in df_lap.columns else pd.Series([0]*len(df_lap))
    speed_data = df_lap['speed']

    # Calculate lateral stress
    lateral_stress = (steering_data.abs() * (speed_data / 150)).mean()
    tire_stress_score = max(100 - lateral_stress * 2, 0)

    # 5. TURN ENTRY ACCURACY (10%) - Smooth steering transitions
    steering_corrections = (steering_data.diff().abs() > 5).sum()
    correction_penalty = (steering_corrections / total_points) * 1000
    turn_entry_score = max(100 - correction_penalty, 0)

    # 6. SECTOR CONSISTENCY (10%) - Check variance across sectors
    max_distance = df_lap['distance'].max()
    sector_length = max_distance / 3
    sector_times = []

    for i in range(3):
        start_dist = i * sector_length
        end_dist = (i + 1) * sector_length
        sector_data = df_lap[(df_lap['distance'] >= start_dist) & (df_lap['distance'] < end_dist)]
        if len(sector_data) >= 2:
            sector_time = (sector_data['timestamp'].max() - sector_data['timestamp'].min()).total_seconds()
            sector_times.append(sector_time)

    if len(sector_times) == 3:
        sector_variance = np.std(sector_times)
        consistency_score = max(100 - sector_variance * 10, 0)
    else:
        consistency_score = 50

    # CALCULATE WEIGHTED CPI
    cpi_score = (
        speed_score * 0.30 +
        brake_score * 0.20 +
        throttle_score * 0.15 +
        tire_stress_score * 0.15 +
        turn_entry_score * 0.10 +
        consistency_score * 0.10
    )

    # CPI Rating
    if cpi_score >= 85:
        rating = "Elite Performance"
        color = "#22c55e"
    elif cpi_score >= 75:
        rating = "Excellent"
        color = "#3b82f6"
    elif cpi_score >= 65:
        rating = "Good"
        color = "#fbbf24"
    elif cpi_score >= 50:
        rating = "Average"
        color = "#f97316"
    else:
        rating = "Needs Improvement"
        color = "#ef4444"

    # Component breakdown for visualization
    components = {
        "Speed Efficiency": round(speed_score, 1),
        "Brake Efficiency": round(brake_score, 1),
        "Throttle Smoothness": round(throttle_score, 1),
        "Tire Management": round(tire_stress_score, 1),
        "Turn Entry": round(turn_entry_score, 1),
        "Consistency": round(consistency_score, 1)
    }

    # Top 3 strengths and weaknesses
    sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)
    strengths = [{"metric": k, "score": v} for k, v in sorted_components[:3]]
    weaknesses = [{"metric": k, "score": v} for k, v in sorted_components[-3:]]

    return {
        "lap": lap,
        "cpi_score": round(cpi_score, 1),
        "rating": rating,
        "color": color,
        "components": components,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": [
            f"Focus on {weaknesses[0]['metric']} to improve CPI by ~{round((100-weaknesses[0]['score'])*0.1, 1)} points"
            if weaknesses[0]['score'] < 70 else "Maintain current performance level",
            f"Excellent {strengths[0]['metric']} - keep this consistent"
        ]
    }

# ============================================
# REAL-TIME STRATEGY SIMULATION (PIT WINDOW)
# ============================================
@app.get("/api/pit_strategy/{lap}")
def get_pit_strategy(lap: int, race_laps: int = 30, fuel_capacity: float = 60.0):
    """
    Real-time pit stop strategy simulator - answers "When should I pit?"

    Uses REAL telemetry data to calculate:
    - Tire degradation rate (from speed loss over laps)
    - Fuel consumption (from throttle usage + lap times)
    - Optimal pit window
    - Overcut/Undercut scenarios
    - Caution (yellow flag) opportunities

    This is NOT post-race analysis - this is RACE ENGINEERING.
    """
    df = load_telemetry()
    weather = load_weather()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    # Get all laps up to current
    available_laps = sorted(df['lap'].unique())
    completed_laps = [l for l in available_laps if l <= lap]

    if not completed_laps:
        raise HTTPException(status_code=404, detail="No lap data")

    # 1. TIRE DEGRADATION ANALYSIS
    lap_times = []
    lap_speeds = []

    for lap_num in completed_laps[-10:]:  # Last 10 laps for trend
        df_lap = df[df['lap'] == lap_num].copy()
        if len(df_lap) > 10:
            lap_time = (df_lap['timestamp'].max() - df_lap['timestamp'].min()).total_seconds()
            avg_speed = df_lap['speed'].mean()
            lap_times.append({"lap": lap_num, "time": lap_time, "avg_speed": avg_speed})
            lap_speeds.append(avg_speed)

    # Calculate tire degradation rate (speed loss per lap)
    if len(lap_speeds) >= 3:
        # Linear regression for degradation
        tire_deg_rate = (lap_speeds[0] - lap_speeds[-1]) / len(lap_speeds)
        tire_deg_pct = (tire_deg_rate / lap_speeds[0]) * 100 if lap_speeds[0] > 0 else 0
    else:
        tire_deg_rate = 0.5  # Default estimate
        tire_deg_pct = 0.3

    # Tire condition estimate (100 = new, 0 = critical)
    laps_on_tires = lap  # Assuming start with new tires
    tire_condition = max(0, 100 - (laps_on_tires * abs(tire_deg_pct)))

    # 2. FUEL CONSUMPTION ANALYSIS
    df_current_lap = df[df['lap'] == lap].copy()
    if not df_current_lap.empty:
        avg_throttle = df_current_lap['ath'].mean() if 'ath' in df_current_lap.columns else 70
        lap_distance = df_current_lap['distance'].max() - df_current_lap['distance'].min()
    else:
        avg_throttle = 70
        lap_distance = 5600  # COTA lap length in meters

    # Fuel consumption model (higher throttle = more fuel)
    # Estimate: ~2L per lap at 70% throttle, scales with throttle usage
    fuel_per_lap = 2.0 * (avg_throttle / 70)
    fuel_remaining = fuel_capacity - (lap * fuel_per_lap)
    laps_of_fuel = fuel_remaining / fuel_per_lap if fuel_per_lap > 0 else 0

    # 3. OPTIMAL PIT WINDOW CALCULATION
    # Factors: tire deg, fuel, pit loss time
    pit_loss_time = 25.0  # Seconds lost in pit (entry, stop, exit)

    # When do tires become critical?
    critical_tire_lap = int(100 / max(abs(tire_deg_pct), 0.5))  # When tire hits 0%
    optimal_tire_lap = int(critical_tire_lap * 0.75)  # Pit at 25% tire life

    # When does fuel run out?
    fuel_critical_lap = lap + int(laps_of_fuel)

    # Recommended pit window (earlier of tire or fuel need)
    recommended_pit_lap = min(optimal_tire_lap, fuel_critical_lap - 2)
    recommended_pit_lap = max(lap + 1, min(recommended_pit_lap, race_laps - 2))

    # 4. OVERCUT/UNDERCUT SCENARIOS
    # Undercut: Pit early, gain track position with fresh tires
    undercut_window = recommended_pit_lap - 2
    undercut_advantage = abs(tire_deg_rate) * 3 * 5.6  # 3 laps faster * lap distance

    # Overcut: Stay out longer, hope for caution or competitors' mistakes
    overcut_window = recommended_pit_lap + 3
    overcut_risk = "High" if tire_condition < 30 else "Medium" if tire_condition < 50 else "Low"

    # 5. CAUTION OPPORTUNITY ANALYSIS
    # Simulate: If caution happens now, should we pit?
    laps_to_go = race_laps - lap
    caution_pit_value = "YES - Pit now!" if tire_condition < 60 and laps_to_go > 10 else "Hold position"

    # 6. WEATHER IMPACT
    track_temp = 35
    if not weather.empty:
        w = weather.iloc[0]
        track_temp = float(w.get('track_temp', w.get('TrackTemp', 35)))

    # High temp = faster tire deg
    temp_multiplier = 1 + (track_temp - 35) * 0.02
    adjusted_pit_lap = int(recommended_pit_lap / temp_multiplier)

    # 7. STRATEGY RECOMMENDATIONS
    strategies = []

    # Strategy 1: Conservative (optimal window)
    strategies.append({
        "name": "Conservative",
        "pit_lap": adjusted_pit_lap,
        "description": "Pit at optimal tire/fuel window",
        "pros": "Safe, predictable, maintains tire performance",
        "cons": "May lose track position temporarily",
        "tire_at_pit": round(100 - (adjusted_pit_lap * abs(tire_deg_pct)), 1),
        "fuel_at_pit": round(fuel_capacity - (adjusted_pit_lap * fuel_per_lap), 1)
    })

    # Strategy 2: Undercut (aggressive)
    if undercut_window > lap:
        strategies.append({
            "name": "Undercut",
            "pit_lap": undercut_window,
            "description": "Pit early to undercut competitors",
            "pros": f"Gain ~{round(undercut_advantage/1000, 1)}km with fresh tires",
            "cons": "Early tire wear in final stint",
            "tire_at_pit": round(100 - (undercut_window * abs(tire_deg_pct)), 1),
            "fuel_at_pit": round(fuel_capacity - (undercut_window * fuel_per_lap), 1)
        })

    # Strategy 3: Overcut (risky)
    if overcut_window <= race_laps - 2:
        strategies.append({
            "name": "Overcut",
            "pit_lap": overcut_window,
            "description": "Stay out longer, pit after competitors",
            "pros": "Gain track position while others pit",
            "cons": f"Risk: {overcut_risk} - tire degradation",
            "tire_at_pit": round(100 - (overcut_window * abs(tire_deg_pct)), 1),
            "fuel_at_pit": round(fuel_capacity - (overcut_window * fuel_per_lap), 1)
        })

    # Final recommendation
    if tire_condition < 20:
        recommendation = "PIT NOW - Critical tire condition!"
        urgency = "critical"
    elif fuel_remaining < fuel_per_lap * 3:
        recommendation = "PIT SOON - Low fuel warning"
        urgency = "high"
    elif lap >= adjusted_pit_lap - 1:
        recommendation = f"Optimal pit window: Lap {adjusted_pit_lap}"
        urgency = "medium"
    else:
        recommendation = f"Stay out - Pit window in {adjusted_pit_lap - lap} laps"
        urgency = "low"

    return {
        "current_lap": lap,
        "race_laps": race_laps,
        "laps_remaining": race_laps - lap,
        "recommendation": recommendation,
        "urgency": urgency,
        "optimal_pit_lap": int(adjusted_pit_lap),
        "tire_analysis": {
            "current_condition": round(tire_condition, 1),
            "degradation_rate": round(abs(tire_deg_rate), 2),
            "degradation_pct_per_lap": round(abs(tire_deg_pct), 2),
            "laps_on_current_tires": laps_on_tires,
            "estimated_critical_lap": int(critical_tire_lap)
        },
        "fuel_analysis": {
            "fuel_remaining": round(fuel_remaining, 1),
            "fuel_per_lap": round(fuel_per_lap, 2),
            "laps_of_fuel_remaining": round(laps_of_fuel, 1),
            "fuel_critical_lap": int(fuel_critical_lap)
        },
        "strategy_options": strategies,
        "undercut_window": int(undercut_window),
        "overcut_window": int(overcut_window),
        "caution_strategy": caution_pit_value,
        "weather_impact": {
            "track_temp": track_temp,
            "temp_multiplier": round(temp_multiplier, 2),
            "impact": "Higher tire wear" if temp_multiplier > 1.1 else "Normal"
        },
        "lap_time_trend": [
            {
                "lap": int(lt["lap"]),
                "time": float(lt["time"]),
                "avg_speed": float(lt["avg_speed"])
            }
            for lt in (lap_times[-5:] if len(lap_times) >= 5 else lap_times)
        ]
    }

# ============================================
# RACE STORY TIMELINE - Automated Race Narrative
# ============================================
@app.get("/api/race_story/{lap}")
def get_race_story(lap: int):
    """
    Generate an automated race story timeline - "What happened in this lap?"

    Analyzes telemetry to detect and timestamp key events:
    - Oversteer/understeer moments
    - Excessive braking
    - Speed losses
    - Perfect sections
    - Gear changes
    - Corner entry/exit issues

    Toyota engineers use this post-race to understand: "What went wrong/right?"
    """
    df = load_telemetry()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    df_lap = df[df['lap'] == lap].copy()
    if df_lap.empty:
        raise HTTPException(status_code=404, detail="Lap not found")

    df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]
    df_lap = df_lap.reset_index(drop=True)

    # Storage for timeline events
    timeline_events = []

    # Get lap reference time
    lap_start_time = df_lap['timestamp'].iloc[0]

    def add_event(idx, event_type, severity, title, description, metrics):
        """Helper to add timeline event"""
        point = df_lap.iloc[idx]
        elapsed = (point['timestamp'] - lap_start_time).total_seconds()

        timeline_events.append({
            "time": round(elapsed, 2),
            "distance": round(point['distance'], 1),
            "lap_progress": round((point['distance'] / df_lap['distance'].max()) * 100, 1),
            "event_type": event_type,
            "severity": severity,
            "title": title,
            "description": description,
            "metrics": metrics,
            "x": float(point['WorldPositionX']) if 'WorldPositionX' in point else 0,
            "y": float(point['WorldPositionY']) if 'WorldPositionY' in point else 0
        })

    # 1. DETECT OVERSTEER (sudden steering corrections)
    if 'Steering_Angle' in df_lap.columns:
        steering_changes = df_lap['Steering_Angle'].diff().abs()
        for idx in range(1, len(df_lap)):
            if steering_changes.iloc[idx] > 10:  # Sudden steering change
                speed = df_lap.iloc[idx]['speed']
                if speed > 100:  # Only at high speed
                    add_event(
                        idx,
                        "oversteer",
                        "warning",
                        "Oversteer Detected",
                        f"Sudden steering correction of {steering_changes.iloc[idx]:.1f}° at {speed:.0f} km/h",
                        {
                            "steering_change": round(steering_changes.iloc[idx], 1),
                            "speed": round(speed, 1)
                        }
                    )

    # 2. DETECT EXCESSIVE BRAKING
    if 'pbrake_f' in df_lap.columns:
        brake_data = df_lap['pbrake_f']
        for idx in range(len(df_lap)):
            if brake_data.iloc[idx] > 85:  # Heavy braking
                speed = df_lap.iloc[idx]['speed']
                add_event(
                    idx,
                    "braking",
                    "info",
                    "Heavy Braking",
                    f"Brake pressure {brake_data.iloc[idx]:.0f}% at {speed:.0f} km/h",
                    {
                        "brake_pressure": round(brake_data.iloc[idx], 1),
                        "speed": round(speed, 1)
                    }
                )

    # 3. DETECT SPEED LOSS ZONES
    if 'speed' in df_lap.columns:
        # Calculate rolling average speed
        df_lap['speed_ma'] = df_lap['speed'].rolling(window=5, center=True).mean()
        speed_drops = df_lap['speed'].diff()

        for idx in range(5, len(df_lap) - 5):
            if speed_drops.iloc[idx] < -15:  # Sudden speed drop
                throttle = df_lap.iloc[idx]['ath'] if 'ath' in df_lap.columns else 0
                if throttle < 50:  # Not under acceleration
                    add_event(
                        idx,
                        "speed_loss",
                        "warning",
                        "Speed Loss",
                        f"Lost {abs(speed_drops.iloc[idx]):.0f} km/h - possible missed apex",
                        {
                            "speed_loss": round(abs(speed_drops.iloc[idx]), 1),
                            "throttle": round(throttle, 1)
                        }
                    )

    # 4. DETECT PERFECT SECTIONS (high speed + high throttle + smooth steering)
    if 'ath' in df_lap.columns and 'Steering_Angle' in df_lap.columns:
        for idx in range(10, len(df_lap) - 10, 20):  # Sample every 20 points
            section = df_lap.iloc[idx-10:idx+10]
            avg_speed = section['speed'].mean()
            avg_throttle = section['ath'].mean()
            steering_smoothness = section['Steering_Angle'].diff().abs().mean()

            if avg_speed > 180 and avg_throttle > 85 and steering_smoothness < 2:
                add_event(
                    idx,
                    "perfect",
                    "success",
                    "Perfect Section",
                    f"Excellent speed ({avg_speed:.0f} km/h) and throttle control ({avg_throttle:.0f}%)",
                    {
                        "avg_speed": round(avg_speed, 1),
                        "avg_throttle": round(avg_throttle, 1),
                        "smoothness": round(steering_smoothness, 2)
                    }
                )

    # 5. DETECT GEAR CHANGES (if available)
    if 'gear' in df_lap.columns:
        gear_changes = df_lap['gear'].diff()
        for idx in range(1, len(df_lap)):
            if abs(gear_changes.iloc[idx]) >= 1:
                gear_from = df_lap.iloc[idx-1]['gear']
                gear_to = df_lap.iloc[idx]['gear']
                speed = df_lap.iloc[idx]['speed']

                # Only log significant gear changes
                if idx % 50 == 0:  # Sample to avoid too many events
                    add_event(
                        idx,
                        "gear_change",
                        "info",
                        f"Gear: {int(gear_from)} → {int(gear_to)}",
                        f"Shifted at {speed:.0f} km/h",
                        {
                            "gear_from": int(gear_from),
                            "gear_to": int(gear_to),
                            "speed": round(speed, 1)
                        }
                    )

    # 6. DETECT CLOSEST TO PERFECT LAP
    # Find the best lap to compare
    try:
        best_lap_info = get_best_lap()
        best_lap_num = best_lap_info['best_lap']

        if best_lap_num != lap:
            df_best = df[df['lap'] == best_lap_num].copy()
            df_best['distance'] = df_best['distance'] - df_best['distance'].iloc[0]

            # Find point where current lap was closest to best lap speed
            common_dist = np.linspace(0, min(df_lap['distance'].max(), df_best['distance'].max()), 50)
            current_speeds = np.interp(common_dist, df_lap['distance'], df_lap['speed'])
            best_speeds = np.interp(common_dist, df_best['distance'], df_best['speed'])
            speed_deltas = current_speeds - best_speeds

            # Find minimum delta (closest to best)
            min_delta_idx = np.argmin(np.abs(speed_deltas))
            min_delta = speed_deltas[min_delta_idx]
            min_delta_dist = common_dist[min_delta_idx]

            # Find index in original lap
            closest_idx = (df_lap['distance'] - min_delta_dist).abs().argmin()

            add_event(
                closest_idx,
                "milestone",
                "success",
                "Closest to Perfect Lap",
                f"Only {abs(min_delta):.1f} km/h from best lap here",
                {
                    "delta": round(min_delta, 1),
                    "best_lap": best_lap_num
                }
            )
    except:
        pass

    # Sort events by time
    timeline_events.sort(key=lambda x: x['time'])

    # Limit to top 20 events to avoid clutter
    if len(timeline_events) > 20:
        # Prioritize: warnings > success > info
        priority_order = {"warning": 0, "success": 1, "info": 2}
        timeline_events.sort(key=lambda x: (priority_order.get(x['severity'], 3), x['time']))
        timeline_events = timeline_events[:20]
        timeline_events.sort(key=lambda x: x['time'])

    # Generate summary
    event_counts = {
        "oversteer": len([e for e in timeline_events if e['event_type'] == 'oversteer']),
        "speed_loss": len([e for e in timeline_events if e['event_type'] == 'speed_loss']),
        "perfect": len([e for e in timeline_events if e['event_type'] == 'perfect']),
        "braking": len([e for e in timeline_events if e['event_type'] == 'braking'])
    }

    # Lap rating
    if event_counts['oversteer'] > 3 or event_counts['speed_loss'] > 5:
        lap_rating = "Challenging"
        rating_color = "#ef4444"
    elif event_counts['perfect'] > 3 and event_counts['oversteer'] < 2:
        lap_rating = "Excellent"
        rating_color = "#22c55e"
    else:
        lap_rating = "Good"
        rating_color = "#fbbf24"

    return {
        "lap": lap,
        "event_count": len(timeline_events),
        "lap_rating": lap_rating,
        "rating_color": rating_color,
        "event_summary": event_counts,
        "timeline": timeline_events,
        "lap_stats": {
            "duration": (df_lap['timestamp'].max() - df_lap['timestamp'].min()).total_seconds(),
            "max_speed": round(df_lap['speed'].max(), 1),
            "avg_speed": round(df_lap['speed'].mean(), 1),
            "distance": round(df_lap['distance'].max(), 1)
        }
    }

# ============================================
# ML MODEL STATUS
# ============================================
@app.get("/api/ml_status")
def get_ml_status():
    """Get status of loaded ML models."""
    return {
        "ml_available": ML_AVAILABLE,
        "models": {
            "anomaly_detector": {
                "loaded": ml_models['anomaly_detector'] is not None,
                "type": "Isolation Forest" if ml_models['anomaly_detector'] else None
            },
            "lap_predictor": {
                "loaded": ml_models['lap_predictor'] is not None,
                "type": "XGBoost/GradientBoosting" if ml_models['lap_predictor'] else None
            },
            "driver_clusterer": {
                "loaded": ml_models['driver_clusterer'] is not None,
                "type": "K-Means Clustering" if ml_models['driver_clusterer'] else None
            }
        },
        "models_dir": MODELS_DIR
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    if not groq_client:
        return {"response": "AI assistant not configured. Set GROQ_API_KEY.", "plot_type": None}

    df = load_telemetry()
    context = ""

    if not df.empty:
        if request.lap:
            df_lap = df[df['lap'] == request.lap]
        else:
            df_lap = df

        if not df_lap.empty:
            context = f"""
Current Telemetry Summary:
- Max Speed: {df_lap['speed'].max():.1f} km/h
- Avg Speed: {df_lap['speed'].mean():.1f} km/h
- Max RPM: {df_lap['nmot'].max():.0f}
- Avg Throttle: {df_lap['ath'].mean():.1f}%
- Max Brake: {df_lap['pbrake_f'].max():.1f}
"""

    system_prompt = """You are GR-Pilot, an AI race engineer assistant for Toyota GR Cup Series.
Provide concise, data-driven analysis. Focus on speed, RPM, throttle, braking, and steering.
Keep responses brief and professional."""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context + "\nQuestion: " + request.message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300,
        )
        text = response.choices[0].message.content

        # Determine plot type
        msg_lower = request.message.lower()
        plot_type = None
        if "speed" in msg_lower:
            plot_type = "speed"
        elif "rpm" in msg_lower or "engine" in msg_lower:
            plot_type = "rpm"
        elif "brake" in msg_lower:
            plot_type = "brake"
        elif "throttle" in msg_lower:
            plot_type = "throttle"

        return {"response": text, "plot_type": plot_type}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "plot_type": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
