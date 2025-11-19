import pydeck as pdk
import pandas as pd
import numpy as np

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculates the bearing between two points."""
    lon_delta_rad = np.radians(lon2 - lon1)
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    
    y = np.sin(lon_delta_rad) * np.cos(lat2_rad)
    x = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(lon_delta_rad)
    
    return np.degrees(np.arctan2(y, x))

def get_car_polygon(lat, lon, bearing, width=2, length=4):
    """Generates a rectangular polygon for the car based on position and bearing."""
    # Convert dimensions to degrees (approx)
    # 1m lat ~ 9e-6 deg, 1m lon ~ 1e-5 deg
    w_deg = width * 1e-5
    l_deg = length * 9e-6
    
    angle_rad = np.radians(bearing)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # Corners relative to center (0,0)
    corners = [
        (length/2, width/2),
        (length/2, -width/2),
        (-length/2, -width/2),
        (-length/2, width/2)
    ]
    
    poly = []
    for cx, cy in corners:
        # Rotate
        rx = cx * cos_a - cy * sin_a
        ry = cx * sin_a + cy * cos_a
        # Translate and convert to degrees
        px = lon + (rx * 1e-5)
        py = lat + (ry * 9e-6)
        poly.append([px, py])
        
    return poly

def plot_3d_track(df, car_index=None):
    """
    Generates a 3D track visualization using PyDeck.
    Uses WorldPositionX/Y (from Dead Reckoning) and Speed for color.
    Optionally highlights a car position if car_index is provided.
    """
    if df.empty or 'WorldPositionX' not in df.columns:
        return None

    # Normalize coordinates for PyDeck
    COTA_LAT = 30.1328
    COTA_LON = -97.6411
    
    # Ensure lat/lon exist
    if 'lat' not in df.columns:
        df['lat'] = COTA_LAT + (df['WorldPositionY'] / 111000)
        df['lon'] = COTA_LON + (df['WorldPositionX'] / 96000)
    
    # Color by Speed
    max_speed = df['speed'].max()
    df['speed_norm'] = df['speed'] / max_speed
    df['color'] = df['speed_norm'].apply(lambda x: [int(x*255), 0, int((1-x)*255), 150])
    
    layers = []
    
    # Layer 1: Track (Wider Scatterplot to simulate road)
    # Using a larger radius to make it look like a road
    layer_track = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position="[lon, lat]",
        get_color="color",
        get_radius=6, # Wider road (6 meters radius)
        pickable=True,
        opacity=0.8,
        stroked=False,
    )
    layers.append(layer_track)
    
    # Layer 2: Car Marker (if index provided)
    if car_index is not None and 0 <= car_index < len(df):
        # Get current and next point to calculate bearing
        current_pt = df.iloc[car_index]
        next_pt = df.iloc[car_index + 1] if car_index + 1 < len(df) else df.iloc[car_index]
        
        bearing = calculate_bearing(current_pt['lat'], current_pt['lon'], next_pt['lat'], next_pt['lon'])
        
        # Create a single row dataframe for the car
        car_df = pd.DataFrame([current_pt])
        car_df['polygon'] = [get_car_polygon(current_pt['lat'], current_pt['lon'], bearing)]
        
        # 3D Car Model (PolygonLayer)
        layer_car = pdk.Layer(
            "PolygonLayer",
            car_df,
            get_polygon="polygon",
            get_fill_color=[255, 255, 255], # White Car
            get_elevation=2, # Car height
            extruded=True,
            wireframe=True,
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
            pickable=True,
            auto_highlight=True,
        )
        layers.append(layer_car)
        
        # Add a spotlight or highlight effect (optional, using a larger translucent circle)
        layer_highlight = pdk.Layer(
            "ScatterplotLayer",
            car_df,
            get_position="[lon, lat]",
            get_color=[255, 255, 255, 50],
            get_radius=15,
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=2,
        )
        layers.append(layer_highlight)

    # View State
    view_state = pdk.ViewState(
        latitude=COTA_LAT,
        longitude=COTA_LON,
        zoom=15, # Closer zoom
        pitch=60, # More tilted for 3D effect
        bearing=0 # We could rotate the camera with the car, but static is safer for now
    )
    
    tooltip = {
        "html": "<b>Speed:</b> {speed} km/h<br><b>Distance:</b> {distance} m",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }
    
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v10"
    )
    
    return r
