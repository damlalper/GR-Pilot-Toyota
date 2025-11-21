import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

import src.data_loader as dl

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- App Initialization ---
app = FastAPI(
    title="GR-Pilot API",
    description="API for providing post-race analytics for the Toyota GR Cup Series.",
    version="1.0.0"
)

# CORS Middleware: Allows the React frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the GR-Pilot API!"}

@app.get("/api/races", response_model=List[str])
def get_races():
    """
    Lists all available races by scanning the COTA directory.
    """
    try:
        race_dirs = [d for d in os.listdir(dl.COTA_DIR) if os.path.isdir(os.path.join(dl.COTA_DIR, d)) and d.startswith("Race")]
        return sorted(race_dirs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="COTA directory not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/api/races/{race_id}/drivers")
def get_drivers(race_id: str):
    """
    Gets the list of drivers for a specific race from the results file.
    Returns a list of dictionaries with driver name and number.
    """
    meta = dl.load_race_meta_data(race_id)
    if 'results' not in meta or meta['results'].empty:
        raise HTTPException(status_code=404, detail=f"Results not found for race '{race_id}'.")
    
    results_df = meta['results']
    
    # Identify the correct columns for driver name and car number
    driver_col = next((c for c in results_df.columns if 'driver' in c.lower()), 'DRIVER_*Extra 3') # Best guess fallback
    number_col = 'NUMBER'
    
    if number_col not in results_df.columns:
        raise HTTPException(status_code=500, detail=f"Could not find '{number_col}' column in results.")

    # Create a clean list of drivers
    drivers = results_df[[driver_col, number_col]].copy()
    drivers.rename(columns={driver_col: 'name', number_col: 'id'}, inplace=True)
    drivers = drivers.dropna(subset=['id'])
    drivers['id'] = drivers['id'].astype(int)
    
    return drivers.to_dict(orient='records')

@app.get("/api/races/{race_id}/drivers/{driver_id}/laps")
def get_laps(race_id: str, driver_id: int):
    """
    Gets the list of all completed lap numbers for a specific driver in a race.
    Note: This is a placeholder. A more accurate implementation would be to get this 
    from the telemetry data itself, as results may not show all laps.
    For now, we get the total laps from the results file.
    """
    meta = dl.load_race_meta_data(race_id)
    if 'results' not in meta or meta['results'].empty:
        raise HTTPException(status_code=404, detail=f"Results not found for race '{race_id}'.")
        
    results_df = meta['results']
    number_col = 'NUMBER'
    laps_col = 'LAPS'
    
    driver_row = results_df[results_df[number_col] == driver_id]
    
    if driver_row.empty:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_id}' not found in results for race '{race_id}'.")
        
    total_laps = driver_row.iloc[0][laps_col]
    
    # Returns a list of numbers from 1 to total_laps
    return list(range(1, total_laps + 1))


@app.get("/api/races/{race_id}/drivers/{driver_id}/laps/{lap_number}/telemetry")
def get_lap_telemetry(race_id: str, driver_id: int, lap_number: int):
    """
    Loads and returns the detailed, processed telemetry data for a single lap.
    """
    logging.info(f"Received request for telemetry: Race={race_id}, Driver={driver_id}, Lap={lap_number}")
    
    df = dl.load_telemetry_for_lap(
        race_id=race_id,
        vehicle_id=str(driver_id),
        lap_number=lap_number
    )
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Telemetry data not found for the specified lap.")
        
    # Convert DataFrame to JSON-friendly format
    # Timestamps can be an issue, so convert them to ISO format strings
    df['timestamp'] = df['timestamp'].dt.isoformat()
    
    return df.to_dict(orient='records')

# To run the app: `uvicorn main:app --reload`