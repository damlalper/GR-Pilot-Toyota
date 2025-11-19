import src.visualizations_3d as v3d
import src.ai_assistant as ai
import src.data_loader as dl
import src.dead_reckoning as dr
import pandas as pd
import os

telemetry_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("1. Loading Telemetry...")
df = dl.load_data(telemetry_path, nrows=10000)
df = dr.generate_track_path(df)

print("\n2. Testing 3D Visualization...")
try:
    chart = v3d.plot_3d_track(df)
    if chart:
        print("   Success: PyDeck chart object created.")
    else:
        print("   Error: Chart object is None.")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. Testing TTS Audio...")
try:
    audio_path = ai.generate_audio("Testing Toyota GR Pilot Audio System.")
    if audio_path and os.path.exists(audio_path):
        print(f"   Success: Audio file generated at {audio_path}")
        # Clean up
        os.remove(audio_path)
    else:
        print("   Error: Audio file generation failed.")
except Exception as e:
    print(f"   Error: {e}")

print("\nVerification Complete.")
