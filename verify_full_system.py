import src.data_loader as dl
import src.analytics as ana
import src.ai_assistant as ai
import pandas as pd

# Paths
telemetry_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"
lap_times_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\COTA_lap_time_R2.csv"
weather_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\26_Weather_ Race 2_Anonymized.CSV"

print("1. Loading Telemetry (Chunk)...")
df = dl.load_data(telemetry_path, nrows=50000)
print(f"   Loaded {len(df)} rows.")

print("\n2. Loading Lap Times...")
df_laps = dl.load_lap_times(lap_times_path)
print(f"   Loaded {len(df_laps)} laps.")

print("\n3. Loading Weather...")
df_weather = dl.load_weather(weather_path)
print(f"   Loaded {len(df_weather)} weather records.")

print("\n4. Testing Anomaly Detection...")
if not df.empty:
    # Simulate two laps
    laps = df['lap'].unique()
    if len(laps) >= 2:
        df_main = df[df['lap'] == laps[0]].copy()
        df_ref = df[df['lap'] == laps[1]].copy()
        
        # Reset distance
        df_main['distance'] = df_main['distance'] - df_main['distance'].iloc[0]
        df_ref['distance'] = df_ref['distance'] - df_ref['distance'].iloc[0]
        
        anomalies = ana.detect_anomalies(df_main, df_ref)
        print(f"   Detected {len(anomalies)} anomalies.")
    else:
        print("   Not enough laps in chunk to test comparison.")
else:
    print("   Telemetry empty.")

print("\n5. Testing AI with Context...")
response = ai.query_ai(df, "Compare my speed", df_ref=df, weather_df=df_weather)
print(f"   AI Response: {response}")

print("\nVerification Complete.")
