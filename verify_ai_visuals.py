import src.ai_assistant as ai
import src.data_loader as dl
import pandas as pd
import plotly.graph_objects as go

telemetry_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"

print("1. Loading Telemetry...")
df = dl.load_data(telemetry_path, nrows=10000)

print("\n2. Testing AI Queries...")
queries = [
    "What is my max speed?",
    "How is my steering?",
    "Check my throttle",
    "Compare my speed"
]

for q in queries:
    print(f"\nQuery: {q}")
    # Mock ref df for comparison
    df_ref = df.copy()
    df_ref['speed'] = df_ref['speed'] * 1.05
    
    response = ai.query_ai(df, q, df_ref=df_ref)
    
    if isinstance(response, dict):
        print(f"   Text: {response['text']}")
        if response['plot']:
            print(f"   Plot: {type(response['plot'])}")
        else:
            print("   Plot: None")
    else:
        print(f"   Response (Old Format): {response}")

print("\nVerification Complete.")
