import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data
def load_data(file_path, vehicle_id=None, nrows=500000):
    """
    Loads telemetry data from CSV.
    Pivots the long-format data to wide-format.
    Calculates Distance from Speed.
    """
    try:
        # Load a chunk of data
        # We need to read enough rows to get a meaningful segment
        df_raw = pd.read_csv(file_path, nrows=nrows)
        
        # Filter by vehicle_id if provided, else pick the first one
        if vehicle_id:
            df_raw = df_raw[df_raw['vehicle_id'] == vehicle_id]
        else:
            unique_vehicles = df_raw['vehicle_id'].unique()
            if len(unique_vehicles) > 0:
                vehicle_id = unique_vehicles[0]
                df_raw = df_raw[df_raw['vehicle_id'] == vehicle_id]
        
        if df_raw.empty:
            return pd.DataFrame()

        # Pivot the data
        # We assume timestamp is the common index. 
        # However, timestamps might be slightly off between sensors.
        # We'll pivot on 'timestamp' and 'telemetry_name'.
        
        # First, ensure timestamp is datetime
        df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
        
        # Pivot
        df_pivot = df_raw.pivot_table(
            index='timestamp', 
            columns='telemetry_name', 
            values='telemetry_value',
            aggfunc='first' # In case of duplicates
        )
        
        # Extract Lap number (it's a column, not a telemetry_name)
        # We group by timestamp and take the first lap value found
        lap_series = df_raw.groupby('timestamp')['lap'].first()
        df_pivot = df_pivot.join(lap_series)
        
        # Forward fill missing values (sensors report at different rates)
        df_pivot = df_pivot.fillna(method='ffill').dropna()
        
        # Reset index to make timestamp a column
        df_pivot = df_pivot.reset_index()
        
        # Ensure numeric types for key columns
        numeric_cols = ['speed', 'nmot', 'Steering_Angle', 'ath', 'pbrake_f', 'pbrake_r', 'accx_can', 'accy_can']
        for col in numeric_cols:
            if col in df_pivot.columns:
                df_pivot[col] = pd.to_numeric(df_pivot[col], errors='coerce')
        
        # Calculate Distance
        # Speed is likely in km/h or m/s. Let's assume km/h for racing.
        # Distance = Speed * Time
        if 'speed' in df_pivot.columns:
            # Calculate time delta in seconds
            df_pivot['time_delta'] = df_pivot['timestamp'].diff().dt.total_seconds().fillna(0)
            
            # Convert speed to m/s (assuming input is km/h)
            # If speed is already m/s, this would be wrong. 
            # Racing telemetry usually uses km/h.
            # Let's assume km/h -> / 3.6
            df_pivot['speed_ms'] = df_pivot['speed'] / 3.6
            
            # Distance in meters
            df_pivot['distance_delta'] = df_pivot['speed_ms'] * df_pivot['time_delta']
            df_pivot['distance'] = df_pivot['distance_delta'].cumsum()
            
        return df_pivot

    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_lap_times(file_path):
    """
    Loads lap times to find the perfect lap.
    """
    try:
        # The file seems to have a complex header or structure based on the cat output.
        # Let's try standard read first, if fails, we might need to skip rows.
        # Based on cat output: "meta_source","meta_time",...
        df = pd.read_csv(file_path)
        # We need 'lap' and 'lap_time' (or similar)
        # Let's standardize column names if needed
        return df
    except Exception as e:
        st.error(f"Error loading lap times: {e}")
        return pd.DataFrame()

@st.cache_data
def load_weather(file_path):
    """
    Loads weather data.
    """
    try:
        # Semicolon separated
        df = pd.read_csv(file_path, sep=';')
        return df
    except Exception as e:
        st.error(f"Error loading weather: {e}")
        return pd.DataFrame()
