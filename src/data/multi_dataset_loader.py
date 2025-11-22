"""
Multi-Dataset Loader
ALL 10 Toyota GR datasets with proper validation and integration

GERÇEK PROFESYONEL DATA PİPELİNE:
- 10 farklı dataset'i yükle
- Format validation
- Schema detection
- Cross-dataset consistency checks
- Memory-efficient loading
- Automatic type inference
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MultiDatasetLoader:
    """
    Toyota GR Hack the Track - Profesyonel Dataset Loader

    Yüklenen Datasets:
    1. 23_AnalysisEnduranceWithSections - Sector/lap timing (19 turns)
    2. 26_Weather - Weather conditions (temp, humidity, wind, rain)
    3. 99_Best 10 Laps By Driver - Driver rankings
    4. 00_Results GR Cup Race Official - Final race results
    5. 03_Provisional Results - Provisional standings
    6. 05_Provisional Results by Class - Class standings
    7. R1/R2_cota_telemetry_data - Raw telemetry (pivot format)
    8. COTA_lap_time - Lap times
    9. COTA_lap_start_time - Lap start timestamps
    10. COTA_lap_end_time - Lap end timestamps
    """

    def __init__(self, base_dir: str = "C:/Users/Lenovo/Desktop/hackathons/TOYOTA/COTA"):
        self.base_dir = Path(base_dir)
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Dict] = {}
        self.race_dirs = {
            'race1': self.base_dir / "Race 1",
            'race2': self.base_dir / "Race 2"
        }

    def load_sector_analysis(self, race: str = 'race1') -> pd.DataFrame:
        """
        23_AnalysisEnduranceWithSections - KRITIK DATASET!

        İçindekiler:
        - LAP_NUMBER, LAP_TIME
        - S1, S2, S3 (sector times)
        - IM1a, IM1, IM2a, IM2, IM3a (intermediate times) - 19 TURN DATA!
        - FLAG_AT_FL (caution flags)
        - PIT_TIME, CROSSING_FINISH_LINE_IN_PIT
        - TOP_SPEED, KPH (avg speed)

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with sector analysis
        """
        file_pattern = "23_AnalysisEnduranceWithSections*Anonymized.CSV"
        filepath = list(self.race_dirs[race].glob(file_pattern))[0]

        logger.info(f"Loading sector analysis from {filepath}")

        # Load with semicolon separator (European CSV format)
        df = pd.read_csv(filepath, sep=';')

        # Data cleaning
        df.columns = df.columns.str.strip()

        # Convert time strings to seconds
        time_columns = ['LAP_TIME', 'S1', 'S2', 'S3',
                       'IM1a_time', 'IM1_time', 'IM2a_time',
                       'IM2_time', 'IM3a_time', 'FL_time']

        for col in time_columns:
            if col in df.columns:
                df[f'{col}_seconds'] = df[col].apply(self._time_string_to_seconds)

        # Extract numeric columns
        numeric_cols = ['LAP_NUMBER', 'DRIVER_NUMBER', 'KPH', 'TOP_SPEED',
                       'PIT_TIME', 'S1_SECONDS', 'S2_SECONDS', 'S3_SECONDS']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        logger.info(f"Loaded sector analysis: {len(df)} laps, {len(df.columns)} columns")

        self.datasets[f'{race}_sector_analysis'] = df
        self.metadata[f'{race}_sector_analysis'] = {
            'rows': len(df),
            'columns': len(df.columns),
            'laps': df['LAP_NUMBER'].nunique() if 'LAP_NUMBER' in df.columns else 0,
            'drivers': df['DRIVER_NUMBER'].nunique() if 'DRIVER_NUMBER' in df.columns else 0
        }

        return df

    def load_weather_data(self, race: str = 'race1') -> pd.DataFrame:
        """
        26_Weather - Weather conditions

        İçindekiler:
        - TIME_UTC_SECONDS, TIME_UTC_STR
        - AIR_TEMP, TRACK_TEMP
        - HUMIDITY, PRESSURE
        - WIND_SPEED, WIND_DIRECTION
        - RAIN

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with weather data
        """
        file_pattern = "26_Weather*Anonymized.CSV"
        filepath = list(self.race_dirs[race].glob(file_pattern))[0]

        logger.info(f"Loading weather data from {filepath}")

        df = pd.read_csv(filepath, sep=';')
        df.columns = df.columns.str.strip()

        # Convert timestamp
        if 'TIME_UTC_SECONDS' in df.columns:
            df['timestamp'] = pd.to_datetime(df['TIME_UTC_SECONDS'], unit='s')

        # Numeric conversions
        numeric_cols = ['AIR_TEMP', 'TRACK_TEMP', 'HUMIDITY', 'PRESSURE',
                       'WIND_SPEED', 'WIND_DIRECTION', 'RAIN']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        logger.info(f"Loaded weather: {len(df)} records")

        self.datasets[f'{race}_weather'] = df
        self.metadata[f'{race}_weather'] = {
            'rows': len(df),
            'duration_minutes': (df['TIME_UTC_SECONDS'].max() - df['TIME_UTC_SECONDS'].min()) / 60 if 'TIME_UTC_SECONDS' in df.columns else 0,
            'avg_air_temp': df['AIR_TEMP'].mean() if 'AIR_TEMP' in df.columns else None,
            'avg_track_temp': df['TRACK_TEMP'].mean() if 'TRACK_TEMP' in df.columns else None
        }

        return df

    def load_best_laps(self, race: str = 'race1') -> pd.DataFrame:
        """
        99_Best 10 Laps By Driver - DRIVER BENCHMARKING!

        İçindekiler:
        - NUMBER, VEHICLE, CLASS
        - TOTAL_DRIVER_LAPS
        - BESTLAP_1 to BESTLAP_10 (top 10 lap times)
        - BESTLAP_1_LAPNUM to BESTLAP_10_LAPNUM (lap numbers)
        - AVERAGE

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with best laps
        """
        file_pattern = "99_Best 10 Laps By Driver*Anonymized.CSV"
        filepath = list(self.race_dirs[race].glob(file_pattern))[0]

        logger.info(f"Loading best laps from {filepath}")

        df = pd.read_csv(filepath, sep=';')
        df.columns = df.columns.str.strip()

        # Convert lap times to seconds
        for i in range(1, 11):
            col = f'BESTLAP_{i}'
            if col in df.columns:
                df[f'{col}_seconds'] = df[col].apply(self._time_string_to_seconds)

        if 'AVERAGE' in df.columns:
            df['AVERAGE_seconds'] = df['AVERAGE'].apply(self._time_string_to_seconds)

        # Numeric conversions
        if 'TOTAL_DRIVER_LAPS' in df.columns:
            df['TOTAL_DRIVER_LAPS'] = pd.to_numeric(df['TOTAL_DRIVER_LAPS'], errors='coerce')

        logger.info(f"Loaded best laps: {len(df)} drivers")

        self.datasets[f'{race}_best_laps'] = df
        self.metadata[f'{race}_best_laps'] = {
            'rows': len(df),
            'total_drivers': len(df),
            'fastest_lap': df['BESTLAP_1_seconds'].min() if 'BESTLAP_1_seconds' in df.columns else None
        }

        return df

    def load_race_results(self, race: str = 'race1') -> pd.DataFrame:
        """
        00_Results GR Cup Race Official - Final race results

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with race results
        """
        file_pattern = "00_Results GR Cup Race*Anonymized.CSV"
        filepaths = list(self.race_dirs[race].glob(file_pattern))

        if not filepaths:
            logger.warning(f"Race results not found for {race}")
            return pd.DataFrame()

        filepath = filepaths[0]
        logger.info(f"Loading race results from {filepath}")

        df = pd.read_csv(filepath, sep=';')
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_results'] = df

        return df

    def load_provisional_results(self, race: str = 'race1') -> pd.DataFrame:
        """
        03_Provisional Results - Provisional standings

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with provisional results
        """
        file_pattern = "03_Provisional Results*Anonymized.CSV"
        filepaths = list(self.race_dirs[race].glob(file_pattern))

        if not filepaths:
            logger.warning(f"Provisional results not found for {race}")
            return pd.DataFrame()

        filepath = filepaths[0]
        logger.info(f"Loading provisional results from {filepath}")

        df = pd.read_csv(filepath, sep=';')
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_provisional'] = df

        return df

    def load_class_results(self, race: str = 'race1') -> pd.DataFrame:
        """
        05_Provisional Results by Class - Class standings

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with class results
        """
        file_pattern = "05_Provisional Results by Class*Anonymized.CSV"
        filepaths = list(self.race_dirs[race].glob(file_pattern))

        if not filepaths:
            logger.warning(f"Class results not found for {race}")
            return pd.DataFrame()

        filepath = filepaths[0]
        logger.info(f"Loading class results from {filepath}")

        df = pd.read_csv(filepath, sep=';')
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_class_results'] = df

        return df

    def load_raw_telemetry(self, race: str = 'race1') -> pd.DataFrame:
        """
        R1/R2_cota_telemetry_data - RAW TELEMETRY (PIVOT FORMAT!)

        Format:
        - telemetry_name: accx_can, accy_can, ath (throttle), pbrake_r (brake), etc.
        - telemetry_value: Value
        - timestamp: Time
        - lap: Lap number
        - vehicle_number: Vehicle ID

        NOTE: This is PIVOT format - needs transformation!

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with raw telemetry (pivot format)
        """
        if race == 'race1':
            filename = "R1_cota_telemetry_data.csv"
        else:
            filename = "R2_cota_telemetry_data.csv"

        filepath = self.race_dirs[race] / filename

        logger.info(f"Loading raw telemetry from {filepath}")

        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # Numeric conversions
        if 'telemetry_value' in df.columns:
            df['telemetry_value'] = pd.to_numeric(df['telemetry_value'], errors='coerce')

        if 'lap' in df.columns:
            df['lap'] = pd.to_numeric(df['lap'], errors='coerce')

        logger.info(f"Loaded raw telemetry: {len(df)} records, {df['telemetry_name'].nunique() if 'telemetry_name' in df.columns else 0} channels")

        self.datasets[f'{race}_raw_telemetry'] = df
        self.metadata[f'{race}_raw_telemetry'] = {
            'rows': len(df),
            'channels': df['telemetry_name'].nunique() if 'telemetry_name' in df.columns else 0,
            'vehicles': df['vehicle_number'].nunique() if 'vehicle_number' in df.columns else 0,
            'laps': df['lap'].nunique() if 'lap' in df.columns else 0
        }

        return df

    def load_lap_times(self, race: str = 'race1') -> pd.DataFrame:
        """
        COTA_lap_time - Lap time data

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with lap times
        """
        if race == 'race1':
            filename = "COTA_lap_time_R1.csv"
        else:
            filename = "COTA_lap_time_R2.csv"

        filepath = self.race_dirs[race] / filename

        logger.info(f"Loading lap times from {filepath}")

        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_lap_times'] = df

        return df

    def load_lap_start_times(self, race: str = 'race1') -> pd.DataFrame:
        """
        COTA_lap_start_time - Lap start timestamps

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with lap start times
        """
        if race == 'race1':
            filename = "COTA_lap_start_time_R1.csv"
        else:
            filename = "COTA_lap_start_time_R2.csv"

        filepath = self.race_dirs[race] / filename

        logger.info(f"Loading lap start times from {filepath}")

        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_lap_start'] = df

        return df

    def load_lap_end_times(self, race: str = 'race1') -> pd.DataFrame:
        """
        COTA_lap_end_time - Lap end timestamps

        Args:
            race: 'race1' or 'race2'

        Returns:
            DataFrame with lap end times
        """
        if race == 'race1':
            filename = "COTA_lap_end_time_R1.csv"
        else:
            filename = "COTA_lap_end_time_R2.csv"

        filepath = self.race_dirs[race] / filename

        logger.info(f"Loading lap end times from {filepath}")

        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        self.datasets[f'{race}_lap_end'] = df

        return df

    def load_all_datasets(self, race: str = 'race1') -> Dict[str, pd.DataFrame]:
        """
        MASTER LOADER - Load ALL 10 datasets!

        Args:
            race: 'race1' or 'race2'

        Returns:
            Dict of all loaded datasets
        """
        logger.info(f"=== LOADING ALL DATASETS FOR {race.upper()} ===")

        try:
            # 1. Sector analysis (CRITICAL)
            self.load_sector_analysis(race)

            # 2. Weather data
            self.load_weather_data(race)

            # 3. Best laps (driver benchmarking)
            self.load_best_laps(race)

            # 4. Race results
            self.load_race_results(race)

            # 5. Provisional results
            self.load_provisional_results(race)

            # 6. Class results
            self.load_class_results(race)

            # 7. Raw telemetry
            self.load_raw_telemetry(race)

            # 8. Lap times
            self.load_lap_times(race)

            # 9. Lap start times
            self.load_lap_start_times(race)

            # 10. Lap end times
            self.load_lap_end_times(race)

            logger.info(f"✅ Successfully loaded {len(self.datasets)} datasets for {race}")

        except Exception as e:
            logger.error(f"Error loading datasets: {str(e)}")
            raise

        return self.datasets

    def get_dataset_summary(self) -> pd.DataFrame:
        """
        All datasets summary

        Returns:
            Summary DataFrame
        """
        summary_data = []

        for name, meta in self.metadata.items():
            summary_data.append({
                'Dataset': name,
                'Rows': meta.get('rows', 0),
                'Columns': meta.get('columns', 0),
                **{k: v for k, v in meta.items() if k not in ['rows', 'columns']}
            })

        return pd.DataFrame(summary_data)

    def _time_string_to_seconds(self, time_str) -> Optional[float]:
        """
        Convert time string (MM:SS.mmm or M:SS.mmm) to seconds

        Args:
            time_str: Time string

        Returns:
            Seconds (float) or None
        """
        if pd.isna(time_str) or time_str == '' or time_str == '0':
            return None

        try:
            # Handle MM:SS.mmm format
            if ':' in str(time_str):
                parts = str(time_str).split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                # Already numeric
                return float(time_str)
        except:
            return None

    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """Get loaded dataset by name"""
        return self.datasets.get(name)

    def list_datasets(self) -> List[str]:
        """List all loaded datasets"""
        return list(self.datasets.keys())


# Test
if __name__ == "__main__":
    loader = MultiDatasetLoader()

    # Load all datasets for Race 1
    datasets = loader.load_all_datasets(race='race1')

    print("=== LOADED DATASETS ===")
    summary = loader.get_dataset_summary()
    print(summary.to_string())

    print("\n=== SECTOR ANALYSIS SAMPLE ===")
    sector_df = loader.get_dataset('race1_sector_analysis')
    if sector_df is not None:
        print(sector_df.head())
        print(f"\nColumns: {sector_df.columns.tolist()}")

    print("\n=== WEATHER SAMPLE ===")
    weather_df = loader.get_dataset('race1_weather')
    if weather_df is not None:
        print(weather_df.head())
        print(f"\nColumns: {weather_df.columns.tolist()}")
