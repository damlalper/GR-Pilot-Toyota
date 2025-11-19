import src.data_loader as dl
import pandas as pd

file_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("Testing load_data...")
df = dl.load_data(file_path, nrows=50000) # Small chunk for testing

if not df.empty:
    print("Data loaded successfully!")
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
    
    if 'lap' in df.columns:
        print("\nLap column found.")
        print("Unique laps:", df['lap'].unique())
    else:
        print("\nERROR: Lap column missing.")
        
    if 'distance' in df.columns:
        print("\nDistance calculated successfully.")
        print("Max distance:", df['distance'].max())
    else:
        print("\nERROR: Distance column missing.")
else:
    print("ERROR: Dataframe is empty.")
