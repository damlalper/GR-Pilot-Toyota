import numpy as np
import pandas as pd

def generate_track_path(df):
    """
    Generates X/Y coordinates using Dead Reckoning (Speed + Steering).
    x = x + v * cos(theta) * dt
    y = y + v * sin(theta) * dt
    theta = theta + (v / L) * tan(delta) * dt  <-- Bicycle model
    
    Simplified: theta += steering * factor * dt
    """
    if df.empty or 'speed' not in df.columns or 'Steering_Angle' not in df.columns:
        return df
    
    # Constants (Estimated for GR86)
    # Steering ratio and wheelbase are unknown, so we use a scaling factor
    # to make the track look reasonable.
    STEERING_FACTOR = 0.002 # Tunable parameter
    
    # Sort by timestamp/distance
    df = df.sort_values('timestamp').copy()
    
    # Calculate dt
    df['dt'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
    
    # Speed in m/s
    v = df['speed'] / 3.6
    
    # Steering in degrees -> radians (assuming input is degrees)
    # Note: Steering_Angle might be steering wheel angle, not tire angle.
    # Ratio is usually ~13:1 to 16:1.
    delta = np.radians(df['Steering_Angle'])
    
    # Heading (Theta)
    # Simple integration: change in heading is proportional to steering * speed * dt
    # d_theta = (v * delta) * factor
    # We'll accumulate changes
    
    # Let's try a simple approach first:
    # heading += steering * dt * speed * constant
    heading_change = delta * v * df['dt'] * STEERING_FACTOR
    df['heading'] = heading_change.cumsum()
    
    # Calculate X/Y
    df['dx'] = v * np.cos(df['heading']) * df['dt']
    df['dy'] = v * np.sin(df['heading']) * df['dt']
    
    df['WorldPositionX'] = df['dx'].cumsum()
    df['WorldPositionY'] = df['dy'].cumsum()
    
    return df
