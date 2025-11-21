"""
Feature Engineering Pipeline for GR-Pilot
Extracts meaningful features from raw telemetry data for ML models.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class TelemetryFeatureEngineer:
    """
    Transforms raw telemetry data into ML-ready features.
    """

    def __init__(self, window_sizes: List[int] = [5, 10, 20]):
        self.window_sizes = window_sizes
        self.feature_columns = []

    def extract_rolling_features(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Extract rolling statistics for a given column."""
        features = pd.DataFrame(index=df.index)

        for window in self.window_sizes:
            # Rolling mean
            features[f'{column}_rolling_mean_{window}'] = df[column].rolling(window=window, min_periods=1).mean()
            # Rolling std (variance indicator)
            features[f'{column}_rolling_std_{window}'] = df[column].rolling(window=window, min_periods=1).std().fillna(0)
            # Rolling min/max
            features[f'{column}_rolling_min_{window}'] = df[column].rolling(window=window, min_periods=1).min()
            features[f'{column}_rolling_max_{window}'] = df[column].rolling(window=window, min_periods=1).max()

        return features

    def extract_derivative_features(self, df: pd.DataFrame, column: str, dt_column: str = 'time_delta') -> pd.DataFrame:
        """Extract rate of change (derivative) features."""
        features = pd.DataFrame(index=df.index)

        # First derivative (rate of change)
        if dt_column in df.columns:
            dt = df[dt_column].replace(0, np.nan)
            features[f'{column}_rate'] = df[column].diff() / dt
        else:
            features[f'{column}_rate'] = df[column].diff()

        # Second derivative (acceleration/jerk)
        features[f'{column}_acceleration'] = features[f'{column}_rate'].diff()

        # Fill NaN
        features = features.fillna(0)

        return features

    def extract_zone_features(self, df: pd.DataFrame, num_zones: int = 10) -> pd.DataFrame:
        """Divide track into zones and extract zone-based statistics."""
        features = pd.DataFrame(index=df.index)

        if 'distance' not in df.columns:
            return features

        max_dist = df['distance'].max()
        zone_length = max_dist / num_zones

        # Assign zone
        df['zone'] = (df['distance'] / zone_length).astype(int).clip(0, num_zones - 1)
        features['zone'] = df['zone']

        # Zone-based aggregations
        for col in ['speed', 'ath', 'pbrake_f']:
            if col in df.columns:
                zone_stats = df.groupby('zone')[col].agg(['mean', 'std', 'max', 'min'])
                zone_stats.columns = [f'{col}_zone_{stat}' for stat in ['mean', 'std', 'max', 'min']]

                # Map back to original index
                for stat_col in zone_stats.columns:
                    features[stat_col] = df['zone'].map(zone_stats[stat_col.split('_zone_')[0] + '_zone_' + stat_col.split('_zone_')[1]])

        return features

    def extract_braking_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract braking-specific features."""
        features = pd.DataFrame(index=df.index)

        if 'pbrake_f' not in df.columns:
            return features

        brake = df['pbrake_f']

        # Braking detection
        features['is_braking'] = (brake > 5).astype(int)
        features['brake_intensity'] = brake.clip(0, 100)

        # Braking events
        braking_start = (features['is_braking'].diff() == 1)
        braking_end = (features['is_braking'].diff() == -1)

        # Cumulative braking events
        features['braking_event_count'] = braking_start.cumsum()

        # Brake pressure buildup rate
        features['brake_buildup_rate'] = brake.diff().clip(lower=0)

        # Trail braking detection (brake + steering)
        if 'Steering_Angle' in df.columns:
            features['trail_braking'] = (brake > 10) & (df['Steering_Angle'].abs() > 20)
            features['trail_braking'] = features['trail_braking'].astype(int)

        return features

    def extract_throttle_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract throttle-specific features."""
        features = pd.DataFrame(index=df.index)

        if 'ath' not in df.columns:
            return features

        throttle = df['ath']

        # Full throttle detection
        features['is_full_throttle'] = (throttle > 95).astype(int)
        features['is_partial_throttle'] = ((throttle > 20) & (throttle < 95)).astype(int)
        features['is_lift_off'] = (throttle < 20).astype(int)

        # Throttle application rate
        features['throttle_rate'] = throttle.diff().fillna(0)
        features['throttle_aggression'] = throttle.diff().abs().rolling(window=10).mean().fillna(0)

        return features

    def extract_cornering_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract cornering-related features."""
        features = pd.DataFrame(index=df.index)

        if 'Steering_Angle' not in df.columns or 'speed' not in df.columns:
            return features

        steering = df['Steering_Angle']
        speed = df['speed']

        # Cornering detection
        features['is_cornering'] = (steering.abs() > 15).astype(int)
        features['corner_direction'] = np.sign(steering)  # -1 left, 1 right

        # Estimated lateral G (simplified: speed^2 * steering / constant)
        features['estimated_lateral_g'] = (speed ** 2) * steering.abs() / 100000

        # Steering rate (how fast driver turns wheel)
        features['steering_rate'] = steering.diff().abs().fillna(0)
        features['steering_smoothness'] = 100 - features['steering_rate'].rolling(window=20).mean().fillna(0).clip(0, 100)

        # Corner entry/exit detection
        corner_entry = (features['is_cornering'].diff() == 1)
        corner_exit = (features['is_cornering'].diff() == -1)
        features['at_corner_entry'] = corner_entry.astype(int)
        features['at_corner_exit'] = corner_exit.astype(int)

        return features

    def extract_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract all features from telemetry data."""
        all_features = df.copy()

        # Basic columns to process
        numeric_cols = ['speed', 'nmot', 'ath', 'pbrake_f', 'Steering_Angle']
        available_cols = [c for c in numeric_cols if c in df.columns]

        # Rolling features
        for col in available_cols:
            rolling_feats = self.extract_rolling_features(df, col)
            all_features = pd.concat([all_features, rolling_feats], axis=1)

        # Derivative features
        for col in available_cols:
            deriv_feats = self.extract_derivative_features(df, col)
            all_features = pd.concat([all_features, deriv_feats], axis=1)

        # Specialized features
        braking_feats = self.extract_braking_features(df)
        throttle_feats = self.extract_throttle_features(df)
        cornering_feats = self.extract_cornering_features(df)
        zone_feats = self.extract_zone_features(df)

        all_features = pd.concat([all_features, braking_feats, throttle_feats, cornering_feats, zone_feats], axis=1)

        # Store feature columns (excluding original data)
        original_cols = set(df.columns)
        self.feature_columns = [c for c in all_features.columns if c not in original_cols]

        return all_features

    def get_feature_matrix(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Return feature matrix and feature names for ML models."""
        features_df = self.extract_all_features(df)
        feature_cols = self.feature_columns

        X = features_df[feature_cols].fillna(0).values
        return X, feature_cols


class LapFeatureAggregator:
    """
    Aggregates point-level features into lap-level features for lap prediction.
    """

    def aggregate_lap_features(self, df: pd.DataFrame) -> Dict:
        """Aggregate telemetry into single lap-level feature vector."""
        features = {}

        # Speed features
        if 'speed' in df.columns:
            features['speed_max'] = df['speed'].max()
            features['speed_mean'] = df['speed'].mean()
            features['speed_std'] = df['speed'].std()
            features['speed_min'] = df['speed'].min()

        # RPM features
        if 'nmot' in df.columns:
            features['rpm_max'] = df['nmot'].max()
            features['rpm_mean'] = df['nmot'].mean()
            features['rpm_std'] = df['nmot'].std()

        # Throttle features
        if 'ath' in df.columns:
            features['throttle_mean'] = df['ath'].mean()
            features['throttle_std'] = df['ath'].std()
            features['full_throttle_pct'] = (df['ath'] > 95).mean() * 100
            features['lift_off_pct'] = (df['ath'] < 20).mean() * 100

        # Brake features
        if 'pbrake_f' in df.columns:
            features['brake_mean'] = df['pbrake_f'].mean()
            features['brake_max'] = df['pbrake_f'].max()
            features['braking_pct'] = (df['pbrake_f'] > 5).mean() * 100
            features['hard_braking_pct'] = (df['pbrake_f'] > 50).mean() * 100

        # Steering features
        if 'Steering_Angle' in df.columns:
            features['steering_mean_abs'] = df['Steering_Angle'].abs().mean()
            features['steering_max_abs'] = df['Steering_Angle'].abs().max()
            features['steering_std'] = df['Steering_Angle'].std()
            features['steering_corrections'] = (df['Steering_Angle'].diff().abs() > 5).sum()

        # Distance
        if 'distance' in df.columns:
            features['total_distance'] = df['distance'].max() - df['distance'].min()

        return features


def create_training_dataset(telemetry_df: pd.DataFrame, laps: List[int]) -> pd.DataFrame:
    """
    Create a training dataset from multiple laps.
    Returns DataFrame with one row per lap.
    """
    aggregator = LapFeatureAggregator()
    rows = []

    for lap in laps:
        lap_data = telemetry_df[telemetry_df['lap'] == lap]
        if len(lap_data) < 10:
            continue

        # Reset distance for each lap
        lap_data = lap_data.copy()
        lap_data['distance'] = lap_data['distance'] - lap_data['distance'].iloc[0]

        # Aggregate features
        features = aggregator.aggregate_lap_features(lap_data)
        features['lap'] = lap

        # Calculate lap time
        if 'timestamp' in lap_data.columns:
            lap_time = (lap_data['timestamp'].max() - lap_data['timestamp'].min()).total_seconds()
            features['lap_time'] = lap_time

        rows.append(features)

    return pd.DataFrame(rows)
