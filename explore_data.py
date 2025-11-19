import pandas as pd
import io

file_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("Reading from middle of file...")
with open(file_path, 'rb') as f:
    f.seek(1000000000) # 1GB offset
    # Read a bit to skip partial line
    f.readline()
    # Read chunk
    chunk = f.read(10000000) # 10MB

df = pd.read_csv(io.BytesIO(chunk), names=['expire_at', 'lap', 'meta_event', 'meta_session', 'meta_source', 'meta_time', 'original_vehicle_id', 'outing', 'telemetry_name', 'telemetry_value', 'timestamp', 'vehicle_id', 'vehicle_number'])

print("\nUnique Telemetry Names in middle:", df['telemetry_name'].unique())
