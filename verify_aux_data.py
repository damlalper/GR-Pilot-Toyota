import src.data_loader as dl
import pandas as pd

lap_times_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\COTA_lap_time_R2.csv"
weather_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\26_Weather_ Race 2_Anonymized.CSV"

print("Checking Lap Times...")
df_laps = dl.load_lap_times(lap_times_path)
if not df_laps.empty:
    print("Columns:", df_laps.columns.tolist())
    print("Head:", df_laps.head(2))
else:
    print("Lap Times Empty")

print("\nChecking Weather...")
df_weather = dl.load_weather(weather_path)
if not df_weather.empty:
    print("Columns:", df_weather.columns.tolist())
    print("Head:", df_weather.head(2))
else:
    print("Weather Empty")
