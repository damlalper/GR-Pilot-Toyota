import pandas as pd

file_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("Checking for specific columns...")
# Read just the header and unique telemetry names
df_head = pd.read_csv(file_path, nrows=100000)
unique_telemetry = df_head['telemetry_name'].unique()

target_columns = ['Laptrigger_lapdist_dls', 'aps', 'VBOX_Lat_Min', 'VBOX_Long_Minutes', 'pbrake_f', 'Steering_Angle']

print("Available Telemetry Names:", unique_telemetry)

for col in target_columns:
    if col in unique_telemetry:
        print(f"[FOUND] {col}")
    else:
        print(f"[MISSING] {col}")
