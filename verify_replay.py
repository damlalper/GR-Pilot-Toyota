import src.visualizations_3d as v3d
import src.data_loader as dl
import src.dead_reckoning as dr
import pandas as pd

telemetry_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("1. Loading Telemetry...")
df = dl.load_data(telemetry_path, nrows=10000)
df = dr.generate_track_path(df)

print("\n2. Testing 3D Replay...")
try:
    # Test with car_index
    chart = v3d.plot_3d_track(df, car_index=500)
    if chart:
        print("   Success: PyDeck chart with Car Marker created.")
        # Verify layers count (should be 2: Track + Car)
        if len(chart.layers) >= 2:
             print(f"   Success: {len(chart.layers)} layers found (Track + Car).")
        else:
             print(f"   Warning: Only {len(chart.layers)} layers found.")
    else:
        print("   Error: Chart object is None.")
except Exception as e:
    print(f"   Error: {e}")

print("\nVerification Complete.")
