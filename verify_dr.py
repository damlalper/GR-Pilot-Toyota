import src.data_loader as dl
import src.dead_reckoning as dr
import pandas as pd

telemetry_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("Loading Telemetry...")
df = dl.load_data(telemetry_path, nrows=10000)

if not df.empty:
    print("Generating Track Path...")
    df = dr.generate_track_path(df)
    
    if 'WorldPositionX' in df.columns and 'WorldPositionY' in df.columns:
        print("Success: WorldPositionX/Y generated.")
        print("X Range:", df['WorldPositionX'].min(), df['WorldPositionX'].max())
        print("Y Range:", df['WorldPositionY'].min(), df['WorldPositionY'].max())
    else:
        print("Error: WorldPositionX/Y not generated.")
else:
    print("Error: Dataframe empty.")
