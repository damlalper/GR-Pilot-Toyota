"""
Telemetry Fusion Engine
Multi-dataset birleştirme ve feature engineering motoru

Bu modül 23 farklı CSV dataset'i birleştirir ve yeni metrikler üretir.
"""

import pandas as pd
import numpy as np
from scipy import signal
from typing import Dict, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class TelemetryFusionEngine:
    """
    Multi-dataset birleştirme ve feature engineering motoru.

    Input: 23 farklı CSV dataset
    Output: Unified telemetry DataFrame + engineered features
    """

    def __init__(self):
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.unified_df: Optional[pd.DataFrame] = None
        self.feature_engineered_df: Optional[pd.DataFrame] = None

    def add_dataset(self, name: str, df: pd.DataFrame) -> None:
        """
        Dataset ekle

        Args:
            name: Dataset ismi
            df: pandas DataFrame
        """
        self.datasets[name] = df
        logger.info(f"Added dataset: {name} ({len(df)} rows, {len(df.columns)} cols)")

    def merge_by_timestamp(
        self,
        base_df: pd.DataFrame,
        merge_df: pd.DataFrame,
        timestamp_col: str = 'TimeStamp',
        tolerance_ms: int = 100
    ) -> pd.DataFrame:
        """
        İki dataset'i timestamp'e göre birleştir

        Args:
            base_df: Ana DataFrame
            merge_df: Birleştirilecek DataFrame
            timestamp_col: Timestamp kolon ismi
            tolerance_ms: Merge toleransı (milisaniye)

        Returns:
            Birleştirilmiş DataFrame
        """
        # Timestamp'leri datetime'a çevir
        if timestamp_col in base_df.columns and timestamp_col in merge_df.columns:
            base_df[timestamp_col] = pd.to_datetime(base_df[timestamp_col], errors='coerce')
            merge_df[timestamp_col] = pd.to_datetime(merge_df[timestamp_col], errors='coerce')

            # Merge asof (nearest timestamp matching)
            merged = pd.merge_asof(
                base_df.sort_values(timestamp_col),
                merge_df.sort_values(timestamp_col),
                on=timestamp_col,
                direction='nearest',
                tolerance=pd.Timedelta(f'{tolerance_ms}ms')
            )

            logger.info(f"Merged datasets: {len(merged)} rows")
            return merged

        else:
            logger.warning(f"Timestamp column '{timestamp_col}' not found, performing simple merge")
            return pd.concat([base_df, merge_df], axis=1)

    def merge_telemetry(self) -> pd.DataFrame:
        """
        Tüm telemetri verilerini birleştir

        Returns:
            Unified DataFrame
        """
        if not self.datasets:
            raise ValueError("No datasets loaded. Use add_dataset() first.")

        # İlk dataset'i base olarak kullan
        dataset_names = list(self.datasets.keys())
        base_df = self.datasets[dataset_names[0]].copy()

        logger.info(f"Using {dataset_names[0]} as base dataset")

        # Diğer dataset'leri merge et
        for i in range(1, len(dataset_names)):
            name = dataset_names[i]
            df = self.datasets[name]

            # Timestamp varsa ona göre, yoksa basit concat
            if 'TimeStamp' in base_df.columns and 'TimeStamp' in df.columns:
                base_df = self.merge_by_timestamp(base_df, df)
            else:
                # Kolon isimlerini conflict önlemek için suffix ekle
                base_df = pd.concat([base_df, df], axis=1)

            logger.info(f"Merged {name}")

        self.unified_df = base_df
        logger.info(f"Final unified dataset: {len(base_df)} rows, {len(base_df.columns)} columns")

        return base_df

    def engineer_features(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Gelişmiş feature engineering - 6 yeni metrik

        Yeni metrikler:
        1. Brake Efficiency Index
        2. Throttle Smoothness
        3. Tire Stress Score
        4. G-Force Magnitude
        5. Turn Entry Quality
        6. Speed Consistency

        Args:
            df: DataFrame (None ise unified_df kullanılır)

        Returns:
            Feature-engineered DataFrame
        """
        if df is None:
            if self.unified_df is None:
                raise ValueError("No unified data. Run merge_telemetry() first.")
            df = self.unified_df.copy()
        else:
            df = df.copy()

        logger.info("Starting feature engineering...")

        # ===== 1. BRAKE EFFICIENCY =====
        if 'Speed' in df.columns and 'BrakePressure' in df.columns:
            df['speed_delta'] = df['Speed'].diff()
            df['brake_efficiency'] = np.where(
                df['BrakePressure'] > 0,
                abs(df['speed_delta']) / (df['BrakePressure'] + 1),  # +1: division by zero önleme
                0
            )
            df['brake_efficiency'] = df['brake_efficiency'].fillna(0).clip(0, 100)
            logger.info("✓ Brake efficiency calculated")

        # ===== 2. THROTTLE SMOOTHNESS =====
        if 'Throttle' in df.columns:
            df['throttle_change'] = df['Throttle'].diff().abs()
            df['throttle_smoothness'] = 100 - (df['throttle_change'].rolling(10, min_periods=1).mean() * 100)
            df['throttle_smoothness'] = df['throttle_smoothness'].fillna(100).clip(0, 100)
            logger.info("✓ Throttle smoothness calculated")

        # ===== 3. G-FORCE MAGNITUDE =====
        if 'LateralAcceleration' in df.columns and 'LongitudinalAcceleration' in df.columns:
            df['g_force_magnitude'] = np.sqrt(
                df['LateralAcceleration']**2 + df['LongitudinalAcceleration']**2
            )
            logger.info("✓ G-force magnitude calculated")
        elif 'Speed' in df.columns:
            # G-force yoksa speed değişiminden tahmin et
            speed_change = df['Speed'].diff()
            time_diff = df.index.to_series().diff().dt.total_seconds().fillna(1)
            df['g_force_magnitude'] = abs(speed_change / time_diff) / 9.81  # m/s^2 to G
            df['g_force_magnitude'] = df['g_force_magnitude'].fillna(0).clip(0, 5)
            logger.info("✓ G-force magnitude estimated from speed")

        # ===== 4. TIRE STRESS SCORE =====
        if 'Speed' in df.columns and 'SteeringAngle' in df.columns:
            speed_norm = df['Speed'] / (df['Speed'].max() + 1)
            steering_norm = abs(df['SteeringAngle']) / (df['SteeringAngle'].abs().max() + 1)

            if 'g_force_magnitude' in df.columns:
                gforce_norm = df['g_force_magnitude'] / (df['g_force_magnitude'].max() + 1)
                df['tire_stress'] = (
                    speed_norm * 0.4 +
                    steering_norm * 0.3 +
                    gforce_norm * 0.3
                ) * 100
            else:
                df['tire_stress'] = (
                    speed_norm * 0.5 +
                    steering_norm * 0.5
                ) * 100

            df['tire_stress'] = df['tire_stress'].fillna(0).clip(0, 100)
            logger.info("✓ Tire stress score calculated")

        # ===== 5. TURN ENTRY QUALITY =====
        if 'SteeringAngle' in df.columns and 'BrakePressure' in df.columns:
            df['is_turn_entry'] = (
                (abs(df['SteeringAngle']) > 5) &
                (df['BrakePressure'] > 20)
            )

            # Trail braking quality: fren + direksiyon koordinasyonu
            df['turn_entry_quality'] = np.where(
                df['is_turn_entry'],
                100 - (abs(df['SteeringAngle'] - df['BrakePressure']/10) * 2),
                100
            )
            df['turn_entry_quality'] = df['turn_entry_quality'].clip(0, 100)
            logger.info("✓ Turn entry quality calculated")

        # ===== 6. SPEED CONSISTENCY =====
        if 'Speed' in df.columns:
            window_size = min(50, len(df) // 10)  # Adaptive window
            df['speed_variance'] = df['Speed'].rolling(window_size, min_periods=1).std()
            df['speed_consistency'] = 100 - (df['speed_variance'] * 5)
            df['speed_consistency'] = df['speed_consistency'].fillna(100).clip(0, 100)
            logger.info("✓ Speed consistency calculated")

        self.feature_engineered_df = df
        logger.info(f"Feature engineering complete: {len(df.columns)} total columns")

        return df

    def detect_anomalies(
        self,
        df: Optional[pd.DataFrame] = None,
        columns: Optional[List[str]] = None,
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        İstatistiksel anomali tespiti (Z-score method)

        Args:
            df: DataFrame (None ise feature_engineered_df kullanılır)
            columns: Kontrol edilecek kolonlar (None ise otomatik)
            threshold: Z-score eşiği (default: 3.0 sigma)

        Returns:
            DataFrame with anomaly flags
        """
        if df is None:
            if self.feature_engineered_df is None:
                raise ValueError("No feature-engineered data available.")
            df = self.feature_engineered_df.copy()
        else:
            df = df.copy()

        if columns is None:
            # Numeric kolonları otomatik seç
            columns = ['Speed', 'BrakePressure', 'Throttle']
            columns = [col for col in columns if col in df.columns]

        logger.info(f"Detecting anomalies in: {columns}")

        for col in columns:
            # Rolling Z-score (100 nokta window)
            window_size = min(100, len(df) // 5)
            rolling_mean = df[col].rolling(window_size, min_periods=1).mean()
            rolling_std = df[col].rolling(window_size, min_periods=1).std()

            df[f'{col}_zscore'] = np.abs(
                (df[col] - rolling_mean) / (rolling_std + 1e-6)  # epsilon: division by zero önleme
            )

            df[f'{col}_anomaly'] = df[f'{col}_zscore'] > threshold

            anomaly_count = df[f'{col}_anomaly'].sum()
            logger.info(f"  {col}: {anomaly_count} anomalies detected ({anomaly_count/len(df)*100:.2f}%)")

        # Total anomaly count
        anomaly_cols = [f'{col}_anomaly' for col in columns]
        df['total_anomalies'] = df[anomaly_cols].sum(axis=1)

        return df

    def calculate_lap_statistics(self, df: pd.DataFrame, lap_col: str = 'LapNumber') -> Dict:
        """
        Tur bazlı istatistikler

        Args:
            df: DataFrame
            lap_col: Tur numarası kolonu

        Returns:
            Dict of lap statistics
        """
        if lap_col not in df.columns:
            logger.warning(f"Lap column '{lap_col}' not found")
            return {}

        lap_stats = {}

        for lap_num in df[lap_col].unique():
            lap_data = df[df[lap_col] == lap_num]

            lap_stats[int(lap_num)] = {
                'avg_speed': lap_data['Speed'].mean() if 'Speed' in lap_data.columns else None,
                'max_speed': lap_data['Speed'].max() if 'Speed' in lap_data.columns else None,
                'avg_brake_pressure': lap_data['BrakePressure'].mean() if 'BrakePressure' in lap_data.columns else None,
                'avg_throttle': lap_data['Throttle'].mean() if 'Throttle' in lap_data.columns else None,
                'anomaly_count': lap_data['total_anomalies'].sum() if 'total_anomalies' in lap_data.columns else 0,
                'data_points': len(lap_data)
            }

        logger.info(f"Calculated statistics for {len(lap_stats)} laps")
        return lap_stats

    def get_feature_summary(self) -> Dict:
        """
        Feature engineering özeti

        Returns:
            Dict with feature statistics
        """
        if self.feature_engineered_df is None:
            return {}

        df = self.feature_engineered_df

        engineered_features = [
            'brake_efficiency', 'throttle_smoothness', 'g_force_magnitude',
            'tire_stress', 'turn_entry_quality', 'speed_consistency'
        ]

        summary = {}
        for feature in engineered_features:
            if feature in df.columns:
                summary[feature] = {
                    'mean': float(df[feature].mean()),
                    'std': float(df[feature].std()),
                    'min': float(df[feature].min()),
                    'max': float(df[feature].max()),
                    'median': float(df[feature].median())
                }

        return summary


# Örnek kullanım
if __name__ == "__main__":
    # Test
    engine = TelemetryFusionEngine()

    # Örnek veri
    test_df = pd.DataFrame({
        'TimeStamp': pd.date_range('2024-01-01', periods=1000, freq='100ms'),
        'Speed': np.random.normal(150, 20, 1000),
        'BrakePressure': np.random.uniform(0, 100, 1000),
        'Throttle': np.random.uniform(0, 100, 1000),
        'SteeringAngle': np.random.normal(0, 15, 1000),
        'LateralAcceleration': np.random.normal(0, 2, 1000),
        'LongitudinalAcceleration': np.random.normal(0, 1, 1000),
        'LapNumber': np.repeat(range(1, 11), 100)
    })

    engine.add_dataset('test_data', test_df)

    # Feature engineering
    enriched_df = engine.engineer_features(test_df)
    print(f"\nEngineered features: {enriched_df.columns.tolist()}")

    # Anomaly detection
    anomaly_df = engine.detect_anomalies(enriched_df)
    print(f"\nTotal anomalies: {anomaly_df['total_anomalies'].sum()}")

    # Lap statistics
    lap_stats = engine.calculate_lap_statistics(anomaly_df)
    print(f"\nLap statistics: {lap_stats}")

    # Feature summary
    summary = engine.get_feature_summary()
    print(f"\nFeature summary: {summary}")
