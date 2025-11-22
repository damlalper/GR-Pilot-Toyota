"""
Data Loader and Validation Module
Güvenli ve robust veri yükleme sistemi
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import streamlit as st

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='gr_pilot.log'
)
logger = logging.getLogger(__name__)


class DataManager:
    """
    Toyota dataset'lerini yüklemek ve validate etmek için merkezi sınıf
    """

    # Beklenen dataset dosya isimleri (23 dataset)
    EXPECTED_DATASETS = [
        "lap_times.csv",
        "telemetry.csv",
        "weather.csv"
        # Gerçek dataset isimlerini ekleyin
    ]

    # Her dataset için beklenen kolonlar
    REQUIRED_COLUMNS = {
        "telemetry.csv": ['Speed', 'BrakePressure', 'Throttle', 'SteeringAngle'],
        "lap_times.csv": ['LapNumber', 'LapTime'],
        "weather.csv": ['Temperature', 'Humidity', 'TrackTemp']
    }

    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize DataManager

        Args:
            data_dir: Raw data klasörü yolu
        """
        self.data_dir = Path(data_dir)
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Dict] = {}

    @st.cache_data(ttl=3600)
    def load_csv_safe(_self, filepath: str) -> pd.DataFrame:
        """
        Güvenli CSV yükleme - crash önleme

        Args:
            filepath: CSV dosya yolu

        Returns:
            pandas DataFrame

        Raises:
            FileNotFoundError: Dosya bulunamadığında
            pd.errors.ParserError: CSV parse hatası
        """
        try:
            logger.info(f"Loading CSV: {filepath}")
            df = pd.read_csv(filepath)

            if df.empty:
                raise ValueError(f"Dataset is empty: {filepath}")

            logger.info(f"Successfully loaded {filepath}: {len(df)} rows, {len(df.columns)} columns")
            return df

        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            st.error(f"❌ Dataset bulunamadı: {filepath}")
            st.stop()

        except pd.errors.ParserError as e:
            logger.error(f"CSV parse error in {filepath}: {str(e)}")
            st.error(f"❌ CSV parse hatası: {filepath}")
            st.stop()

        except Exception as e:
            logger.error(f"Unexpected error loading {filepath}: {str(e)}")
            st.error(f"❌ Beklenmeyen hata: {type(e).__name__}")
            st.stop()

    def validate_columns(self, df: pd.DataFrame, expected_cols: List[str], dataset_name: str) -> bool:
        """
        Dataset kolonlarını validate et

        Args:
            df: DataFrame
            expected_cols: Beklenen kolon listesi
            dataset_name: Dataset ismi (hata mesajları için)

        Returns:
            True if valid, raises exception if not
        """
        missing_cols = [col for col in expected_cols if col not in df.columns]

        if missing_cols:
            error_msg = f"Missing columns in {dataset_name}: {missing_cols}"
            logger.error(error_msg)
            st.error(f"❌ {error_msg}")
            st.info(f"Available columns: {df.columns.tolist()}")
            raise ValueError(error_msg)

        return True

    def validate_data_types(self, df: pd.DataFrame, dataset_name: str) -> bool:
        """
        Veri tiplerini validate et

        Args:
            df: DataFrame
            dataset_name: Dataset ismi

        Returns:
            True if valid
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Speed, Brake, Throttle gibi kolonlar numeric olmalı
        for col in ['Speed', 'BrakePressure', 'Throttle']:
            if col in df.columns and col not in numeric_cols:
                logger.warning(f"{col} in {dataset_name} is not numeric, attempting conversion")
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    st.warning(f"⚠️ {col} numeric'e çevrilemedi")

        return True

    def detect_outliers(self, df: pd.DataFrame, column: str, threshold: float = 3.0) -> pd.Series:
        """
        Z-score ile outlier tespiti

        Args:
            df: DataFrame
            column: Kontrol edilecek kolon
            threshold: Z-score eşiği (default: 3.0)

        Returns:
            Boolean Series (True = outlier)
        """
        if column not in df.columns:
            return pd.Series([False] * len(df))

        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        return z_scores > threshold

    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Dataset özet istatistikleri

        Args:
            df: DataFrame

        Returns:
            Summary dict
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum()
        }

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Tüm dataset'leri yükle ve validate et

        Returns:
            Dict of DataFrames
        """
        loaded_datasets = {}

        for dataset_file in self.EXPECTED_DATASETS:
            filepath = self.data_dir / dataset_file

            if not filepath.exists():
                logger.warning(f"Dataset not found: {dataset_file}")
                continue

            # Load
            df = self.load_csv_safe(str(filepath))

            # Validate columns
            if dataset_file in self.REQUIRED_COLUMNS:
                self.validate_columns(df, self.REQUIRED_COLUMNS[dataset_file], dataset_file)

            # Validate data types
            self.validate_data_types(df, dataset_file)

            # Store
            loaded_datasets[dataset_file] = df
            self.metadata[dataset_file] = self.get_data_summary(df)

            logger.info(f"Loaded and validated: {dataset_file}")

        self.datasets = loaded_datasets
        return loaded_datasets

    def load_from_upload(self, uploaded_file) -> Tuple[pd.DataFrame, str]:
        """
        Streamlit file uploader'dan veri yükle

        Args:
            uploaded_file: Streamlit UploadedFile object

        Returns:
            (DataFrame, filename)
        """
        try:
            filename = uploaded_file.name
            df = pd.read_csv(uploaded_file)

            logger.info(f"Loaded uploaded file: {filename} ({len(df)} rows)")

            return df, filename

        except Exception as e:
            logger.error(f"Error loading uploaded file: {str(e)}")
            st.error(f"❌ Dosya yüklenemedi: {type(e).__name__}")
            raise

    def get_dataset(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Yüklenmiş dataset'i al

        Args:
            dataset_name: Dataset ismi

        Returns:
            DataFrame or None
        """
        return self.datasets.get(dataset_name)

    def list_available_datasets(self) -> List[str]:
        """
        Yüklenmiş dataset'lerin listesi

        Returns:
            List of dataset names
        """
        return list(self.datasets.keys())

    def get_metadata(self, dataset_name: str) -> Optional[Dict]:
        """
        Dataset metadata'sını al

        Args:
            dataset_name: Dataset ismi

        Returns:
            Metadata dict or None
        """
        return self.metadata.get(dataset_name)


# Örnek kullanım
if __name__ == "__main__":
    manager = DataManager(data_dir="data")

    # Tüm dataset'leri yükle
    datasets = manager.load_all_datasets()

    print(f"Loaded {len(datasets)} datasets:")
    for name, df in datasets.items():
        print(f"  - {name}: {len(df)} rows")
        print(f"    Metadata: {manager.get_metadata(name)}")
