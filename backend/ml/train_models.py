"""
Model Training Script for GR-Pilot
Trains all ML models on COTA Race 2 telemetry data.
"""
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.feature_engineering import TelemetryFeatureEngineer, create_training_dataset
from ml.anomaly_model import DrivingAnomalyDetector, train_anomaly_detector
from ml.lap_predictor import LapTimePredictor, train_lap_predictor
from ml.driver_clustering import DriverStyleClusterer, train_driver_clusterer

# Paths
DATA_DIR = r"C:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2"
TELEMETRY_PATH = os.path.join(DATA_DIR, "R2_cota_telemetry_data.csv")
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_models")

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)


def load_telemetry_data(nrows: int = 500000) -> pd.DataFrame:
    """Load and preprocess telemetry data."""
    print(f"Loading telemetry from {TELEMETRY_PATH}...")

    df_raw = pd.read_csv(TELEMETRY_PATH, nrows=nrows)
    print(f"Loaded {len(df_raw)} rows")

    # Filter to single vehicle for consistency
    unique_vehicles = df_raw['vehicle_id'].unique()
    print(f"Found {len(unique_vehicles)} vehicles: {unique_vehicles[:5]}")

    if len(unique_vehicles) > 0:
        df_raw = df_raw[df_raw['vehicle_id'] == unique_vehicles[0]]
        print(f"Filtered to vehicle {unique_vehicles[0]}: {len(df_raw)} rows")

    # Parse timestamps
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])

    # Pivot to wide format
    print("Pivoting to wide format...")
    df_pivot = df_raw.pivot_table(
        index='timestamp',
        columns='telemetry_name',
        values='telemetry_value',
        aggfunc='first'
    )

    # Add lap column
    lap_series = df_raw.groupby('timestamp')['lap'].first()
    df_pivot = df_pivot.join(lap_series)

    # Forward fill and clean
    df_pivot = df_pivot.ffill().dropna()
    df_pivot = df_pivot.reset_index()

    # Convert numeric columns
    numeric_cols = ['speed', 'nmot', 'Steering_Angle', 'ath', 'pbrake_f', 'pbrake_r', 'accx_can', 'accy_can', 'gear']
    for col in numeric_cols:
        if col in df_pivot.columns:
            df_pivot[col] = pd.to_numeric(df_pivot[col], errors='coerce')

    # Calculate distance
    if 'speed' in df_pivot.columns:
        df_pivot['time_delta'] = df_pivot['timestamp'].diff().dt.total_seconds().fillna(0)
        df_pivot['speed_ms'] = df_pivot['speed'] / 3.6
        df_pivot['distance_delta'] = df_pivot['speed_ms'] * df_pivot['time_delta']
        df_pivot['distance'] = df_pivot['distance_delta'].cumsum()

    print(f"Final dataset: {len(df_pivot)} rows, {len(df_pivot.columns)} columns")
    print(f"Laps: {sorted(df_pivot['lap'].unique())}")

    return df_pivot


def train_all_models(df: pd.DataFrame):
    """Train all ML models."""

    laps = sorted(df['lap'].unique())
    print(f"\n{'='*60}")
    print(f"Training ML models on {len(laps)} laps")
    print(f"{'='*60}")

    # 1. Train Anomaly Detector
    print("\n[1/3] Training Anomaly Detector (Isolation Forest)...")
    try:
        anomaly_detector = train_anomaly_detector(df, laps)
        anomaly_path = os.path.join(MODELS_DIR, "anomaly_detector.pkl")
        anomaly_detector.save(anomaly_path)
        print(f"✓ Anomaly detector saved to {anomaly_path}")
    except Exception as e:
        print(f"✗ Anomaly detector training failed: {e}")

    # 2. Train Lap Time Predictor
    print("\n[2/3] Training Lap Time Predictor (XGBoost/GradientBoosting)...")
    try:
        lap_predictor, metrics = train_lap_predictor(df, laps)
        predictor_path = os.path.join(MODELS_DIR, "lap_predictor.pkl")
        lap_predictor.save(predictor_path)
        print(f"✓ Lap predictor saved to {predictor_path}")
        print(f"  MAE: {metrics['mae']:.2f}s, R2: {metrics['r2']:.3f}")
    except Exception as e:
        print(f"✗ Lap predictor training failed: {e}")

    # 3. Train Driver Clusterer
    print("\n[3/3] Training Driver Style Clusterer (K-Means)...")
    try:
        driver_clusterer = train_driver_clusterer(df, laps)
        clusterer_path = os.path.join(MODELS_DIR, "driver_clusterer.pkl")
        driver_clusterer.save(clusterer_path)
        print(f"✓ Driver clusterer saved to {clusterer_path}")
        print(f"  Clusters: {driver_clusterer.n_clusters}")
        for cid, profile in driver_clusterer.cluster_profiles.items():
            print(f"    Cluster {cid}: {profile['style_name']} ({profile['sample_count']} samples)")
    except Exception as e:
        print(f"✗ Driver clusterer training failed: {e}")

    print(f"\n{'='*60}")
    print("Model training complete!")
    print(f"Models saved in: {MODELS_DIR}")
    print(f"{'='*60}")


def test_models(df: pd.DataFrame):
    """Test trained models on sample data."""
    print("\n--- Testing Trained Models ---")

    # Get a sample lap
    sample_lap = df['lap'].unique()[len(df['lap'].unique()) // 2]
    df_sample = df[df['lap'] == sample_lap].copy()
    df_sample['distance'] = df_sample['distance'] - df_sample['distance'].iloc[0]

    # Test Anomaly Detector
    anomaly_path = os.path.join(MODELS_DIR, "anomaly_detector.pkl")
    if os.path.exists(anomaly_path):
        detector = DrivingAnomalyDetector()
        detector.load(anomaly_path)
        report = detector.get_anomaly_report(df_sample)
        print(f"\nAnomaly Detector Test (Lap {sample_lap}):")
        print(f"  Anomalies found: {report['anomaly_count']} / {report['total_points']} points ({report['anomaly_percentage']:.2f}%)")

    # Test Lap Predictor
    predictor_path = os.path.join(MODELS_DIR, "lap_predictor.pkl")
    if os.path.exists(predictor_path):
        predictor = LapTimePredictor()
        predictor.load(predictor_path)
        predicted_time = predictor.predict_from_telemetry(df_sample)
        actual_time = (df_sample['timestamp'].max() - df_sample['timestamp'].min()).total_seconds()
        print(f"\nLap Time Predictor Test (Lap {sample_lap}):")
        print(f"  Actual: {actual_time:.2f}s, Predicted: {predicted_time:.2f}s, Error: {abs(actual_time - predicted_time):.2f}s")

    # Test Driver Clusterer
    clusterer_path = os.path.join(MODELS_DIR, "driver_clusterer.pkl")
    if os.path.exists(clusterer_path):
        clusterer = DriverStyleClusterer()
        clusterer.load(clusterer_path)
        dna = clusterer.get_driver_dna(df_sample)
        print(f"\nDriver DNA Test (Lap {sample_lap}):")
        print(f"  Style: {dna['style_name']}")
        print(f"  Scores: Aggression={dna['dna_scores']['aggression']}, Smoothness={dna['dna_scores']['smoothness']}, Consistency={dna['dna_scores']['consistency']}")


if __name__ == "__main__":
    # Load data
    df = load_telemetry_data(nrows=1000000)  # Load 1M rows

    # Train models
    train_all_models(df)

    # Test models
    test_models(df)
