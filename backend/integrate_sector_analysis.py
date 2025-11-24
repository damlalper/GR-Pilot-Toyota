"""
Sector Analysis Integration Script
Adds sector-by-sector performance analysis to backend API
"""
import pandas as pd
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SECTOR_PATH = r"C:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\23_AnalysisEnduranceWithSections_ Race 2_Anonymized.CSV"

def analyze_sector_data():
    """Analyze sector CSV structure"""
    df = pd.read_csv(SECTOR_PATH, sep=';')

    print("=" * 80)
    print("SECTOR ANALYSIS INTEGRATION")
    print("=" * 80)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nKey Columns:")
    key_cols = ['NUMBER', ' DRIVER_NUMBER', ' LAP_NUMBER', ' LAP_TIME',
                ' S1', ' S2', ' S3', ' KPH', 'TOP_SPEED',
                'IM1a_time', 'IM1_time', 'IM2a_time', 'IM2_time', 'IM3a_time']

    for col in key_cols:
        if col in df.columns:
            print(f"  - {col}: {df[col].dtype}")

    print("\nSample Data (Lap 1, Vehicle 7):")
    sample = df[(df['NUMBER'] == 7) & (df[' LAP_NUMBER'] == 1)]
    print(sample[['NUMBER', ' LAP_NUMBER', ' LAP_TIME', ' S1', ' S2', ' S3', ' KPH']].to_string())

    print("\nIntermediate Times Availability:")
    im_cols = [c for c in df.columns if 'IM' in c]
    print(f"Found {len(im_cols)} intermediate timing columns:")
    for col in im_cols:
        non_null = df[col].notna().sum()
        print(f"  - {col}: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}% populated)")

    print("\nSector Statistics:")
    print(f"Unique vehicles: {df['NUMBER'].nunique()}")
    print(f"Total laps: {df[' LAP_NUMBER'].max()}")
    print(f"Average S1 time: {pd.to_datetime(df[' S1'], format='%M:%S.%f', errors='coerce').dt.second.mean():.2f}s")

    return df

def create_sector_endpoint_code():
    """Generate endpoint code"""
    code = '''
# Add to backend/main.py

@app.get("/api/sectors/{lap}")
def get_sector_analysis(lap: int, vehicle_number: Optional[int] = None):
    """
    Get sector-by-sector analysis for a specific lap.
    Returns intermediate times, sector times, top speeds.
    """
    try:
        df = pd.read_csv(SECTORS_PATH, sep=';')

        # Filter by lap
        df_lap = df[df[' LAP_NUMBER'] == lap].copy()

        if vehicle_number:
            df_lap = df_lap[df_lap['NUMBER'] == vehicle_number]

        if df_lap.empty:
            raise HTTPException(status_code=404, detail=f"No sector data for lap {lap}")

        # Parse times
        time_cols = [' LAP_TIME', ' S1', ' S2', ' S3']
        for col in time_cols:
            if col in df_lap.columns:
                df_lap[col + '_seconds'] = pd.to_timedelta('00:' + df_lap[col].astype(str)).dt.total_seconds()

        # Structure response
        results = []
        for _, row in df_lap.iterrows():
            results.append({
                "vehicle_number": int(row['NUMBER']),
                "lap": int(row[' LAP_NUMBER']),
                "lap_time": str(row[' LAP_TIME']),
                "lap_time_seconds": float(row[' LAP_TIME_seconds']) if ' LAP_TIME_seconds' in df_lap.columns else None,
                "sectors": {
                    "s1": {
                        "time": str(row[' S1']),
                        "seconds": float(row['S1_SECONDS']) if 'S1_SECONDS' in df_lap.columns else None,
                        "improvement": int(row[' S1_IMPROVEMENT'])
                    },
                    "s2": {
                        "time": str(row[' S2']),
                        "seconds": float(row['S2_SECONDS']) if 'S2_SECONDS' in df_lap.columns else None,
                        "improvement": int(row[' S2_IMPROVEMENT'])
                    },
                    "s3": {
                        "time": str(row[' S3']),
                        "seconds": float(row['S3_SECONDS']) if 'S3_SECONDS' in df_lap.columns else None,
                        "improvement": int(row[' S3_IMPROVEMENT'])
                    }
                },
                "speed": {
                    "average_kph": float(row[' KPH']),
                    "top_speed": float(row['TOP_SPEED']) if 'TOP_SPEED' in row and pd.notna(row['TOP_SPEED']) else None
                },
                "intermediates": {
                    "im1a": float(row['IM1a_time']) if 'IM1a_time' in row and pd.notna(row['IM1a_time']) else None,
                    "im1": float(row['IM1_time']) if 'IM1_time' in row and pd.notna(row['IM1_time']) else None,
                    "im2a": float(row['IM2a_time']) if 'IM2a_time' in row and pd.notna(row['IM2a_time']) else None,
                    "im2": float(row['IM2_time']) if 'IM2_time' in row and pd.notna(row['IM2_time']) else None,
                    "im3a": float(row['IM3a_time']) if 'IM3a_time' in row and pd.notna(row['IM3a_time']) else None
                },
                "pit_time": float(row['PIT_TIME']) if 'PIT_TIME' in row and pd.notna(row['PIT_TIME']) else None
            })

        return {
            "lap": lap,
            "vehicle_count": len(results),
            "data": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sector data: {str(e)}")

@app.get("/api/sectors/compare")
def compare_sectors(lap1: int, lap2: int, vehicle_number: int):
    """Compare two laps sector-by-sector"""
    data1 = get_sector_analysis(lap1, vehicle_number)
    data2 = get_sector_analysis(lap2, vehicle_number)

    if not data1['data'] or not data2['data']:
        raise HTTPException(status_code=404, detail="One or both laps not found")

    lap1_data = data1['data'][0]
    lap2_data = data2['data'][0]

    return {
        "vehicle_number": vehicle_number,
        "lap1": lap1,
        "lap2": lap2,
        "comparison": {
            "lap_time_delta": lap1_data['lap_time_seconds'] - lap2_data['lap_time_seconds'],
            "sector_deltas": {
                "s1": lap1_data['sectors']['s1']['seconds'] - lap2_data['sectors']['s1']['seconds'],
                "s2": lap1_data['sectors']['s2']['seconds'] - lap2_data['sectors']['s2']['seconds'],
                "s3": lap1_data['sectors']['s3']['seconds'] - lap2_data['sectors']['s3']['seconds']
            },
            "faster_lap": lap1 if lap1_data['lap_time_seconds'] < lap2_data['lap_time_seconds'] else lap2
        }
    }
'''
    return code

if __name__ == "__main__":
    # Analyze data
    df = analyze_sector_data()

    # Generate code
    print("\n" + "=" * 80)
    print("GENERATED ENDPOINT CODE (Add to backend/main.py)")
    print("=" * 80)
    code = create_sector_endpoint_code()
    print(code)

    # Save to file
    with open('sector_endpoints.txt', 'w') as f:
        f.write(code)
    print("\nCode saved to: sector_endpoints.txt")
