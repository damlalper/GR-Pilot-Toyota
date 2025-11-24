import pandas as pd

# Check telemetry columns
df = pd.read_csv(r"C:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv", nrows=100000)

print("=== TELEMETRY COLUMNS ===")
print(df.columns.tolist())

print("\n=== UNIQUE TELEMETRY_NAME VALUES ===")
print(sorted(df['telemetry_name'].unique()))

print("\n=== GPS/LOCATION CHECK ===")
gps_channels = [c for c in df['telemetry_name'].unique() if 'gps' in c.lower() or 'lat' in c.lower() or 'lon' in c.lower() or 'position' in c.lower()]
print(f"GPS channels found: {gps_channels}")

print("\n=== SAMPLE DATA ===")
print(df.head(20))
