import pandas as pd
import numpy as np

def detect_anomalies(df_main, df_ref, speed_threshold=15.0):
    """
    Detects anomalies where the main driver is significantly slower than the reference.
    Logic: (Ref_Speed - Main_Speed) > threshold
    Returns a DataFrame of anomalies.
    """
    if df_main.empty or df_ref is None or df_ref.empty:
        return pd.DataFrame()
    
    # We need to align data by Distance
    # Since distance steps might not match exactly, we use interpolation or binning.
    # For simplicity/speed in prototype, we'll merge_asof or reindex.
    
    # Let's use interpolation on a common distance grid
    # Create a common distance axis based on the reference lap
    common_distance = df_ref['distance']
    
    # Interpolate Main Speed to Ref Distance
    main_speed_interp = np.interp(common_distance, df_main['distance'], df_main['speed'])
    
    # Calculate Delta
    # Positive Delta = Ref is faster (Main is slower) -> Anomaly
    speed_delta = df_ref['speed'] - main_speed_interp
    
    # Find Anomalies
    anomalies = df_ref[speed_delta > speed_threshold].copy()
    anomalies['speed_delta'] = speed_delta[speed_delta > speed_threshold]
    anomalies['main_speed'] = main_speed_interp[speed_delta > speed_threshold]
    
    return anomalies
