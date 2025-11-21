"""
Anomaly Detection Model for GR-Pilot
Uses Isolation Forest to detect unusual driving patterns.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import pickle
import os

from .feature_engineering import TelemetryFeatureEngineer


class DrivingAnomalyDetector:
    """
    Detects anomalies in driving telemetry using Isolation Forest.
    Anomalies can indicate:
    - Unusual braking patterns
    - Inconsistent throttle application
    - Erratic steering
    - Potential mechanical issues
    - Driver mistakes
    """

    def __init__(self, contamination: float = 0.05, n_estimators: int = 100):
        """
        Initialize the anomaly detector.

        Args:
            contamination: Expected proportion of anomalies (0.05 = 5%)
            n_estimators: Number of trees in the forest
        """
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_engineer = TelemetryFeatureEngineer()
        self.is_fitted = False
        self.feature_names = []

    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare feature matrix from telemetry data."""
        # Select key features for anomaly detection
        feature_cols = []

        # Speed-based features
        if 'speed' in df.columns:
            df['speed_diff'] = df['speed'].diff().fillna(0)
            df['speed_diff_abs'] = df['speed_diff'].abs()
            feature_cols.extend(['speed', 'speed_diff', 'speed_diff_abs'])

        # Throttle features
        if 'ath' in df.columns:
            df['throttle_diff'] = df['ath'].diff().fillna(0)
            feature_cols.extend(['ath', 'throttle_diff'])

        # Brake features
        if 'pbrake_f' in df.columns:
            df['brake_diff'] = df['pbrake_f'].diff().fillna(0)
            feature_cols.extend(['pbrake_f', 'brake_diff'])

        # Steering features
        if 'Steering_Angle' in df.columns:
            df['steering_diff'] = df['Steering_Angle'].diff().fillna(0)
            df['steering_abs'] = df['Steering_Angle'].abs()
            feature_cols.extend(['Steering_Angle', 'steering_diff', 'steering_abs'])

        # Combined features (driver behavior patterns)
        if 'ath' in df.columns and 'pbrake_f' in df.columns:
            # Simultaneous throttle and brake (unusual unless trail braking)
            df['throttle_brake_overlap'] = df['ath'] * df['pbrake_f'] / 100
            feature_cols.append('throttle_brake_overlap')

        if 'speed' in df.columns and 'Steering_Angle' in df.columns:
            # High speed with high steering (risky)
            df['speed_steering_risk'] = df['speed'] * df['Steering_Angle'].abs() / 1000
            feature_cols.append('speed_steering_risk')

        self.feature_names = feature_cols
        X = df[feature_cols].fillna(0).values
        return X

    def fit(self, df: pd.DataFrame) -> 'DrivingAnomalyDetector':
        """
        Fit the anomaly detector on training data.

        Args:
            df: Telemetry DataFrame with columns like speed, ath, pbrake_f, Steering_Angle
        """
        X = self._prepare_features(df.copy())

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit isolation forest
        self.model.fit(X_scaled)
        self.is_fitted = True

        print(f"Anomaly detector fitted on {len(X)} samples with {len(self.feature_names)} features")
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomalies in telemetry data.

        Args:
            df: Telemetry DataFrame

        Returns:
            DataFrame with anomaly scores and labels
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        df_copy = df.copy()
        X = self._prepare_features(df_copy)
        X_scaled = self.scaler.transform(X)

        # Get anomaly predictions (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(X_scaled)

        # Get anomaly scores (lower = more anomalous)
        scores = self.model.decision_function(X_scaled)

        # Add to dataframe
        df_copy['anomaly_label'] = predictions
        df_copy['anomaly_score'] = scores
        df_copy['is_anomaly'] = (predictions == -1).astype(int)

        return df_copy

    def get_anomaly_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a comprehensive anomaly report.

        Args:
            df: Telemetry DataFrame with predictions

        Returns:
            Dictionary with anomaly statistics and details
        """
        if 'is_anomaly' not in df.columns:
            df = self.predict(df)

        anomalies = df[df['is_anomaly'] == 1]

        report = {
            'total_points': len(df),
            'anomaly_count': len(anomalies),
            'anomaly_percentage': len(anomalies) / len(df) * 100 if len(df) > 0 else 0,
            'anomalies': []
        }

        # Categorize anomalies
        for idx, row in anomalies.iterrows():
            anomaly_info = {
                'index': idx,
                'distance': float(row.get('distance', 0)),
                'anomaly_score': float(row['anomaly_score']),
                'speed': float(row.get('speed', 0)),
                'throttle': float(row.get('ath', 0)),
                'brake': float(row.get('pbrake_f', 0)),
                'steering': float(row.get('Steering_Angle', 0)),
            }

            # Determine anomaly type based on feature values
            anomaly_type = self._classify_anomaly(row)
            anomaly_info['type'] = anomaly_type
            anomaly_info['explanation'] = self._explain_anomaly(row, anomaly_type)

            report['anomalies'].append(anomaly_info)

        # Sort by severity (anomaly score)
        report['anomalies'] = sorted(report['anomalies'], key=lambda x: x['anomaly_score'])

        return report

    def _classify_anomaly(self, row: pd.Series) -> str:
        """Classify the type of anomaly based on telemetry values."""
        speed_diff = abs(row.get('speed_diff', 0))
        throttle_diff = abs(row.get('throttle_diff', 0))
        brake_diff = abs(row.get('brake_diff', 0))
        steering_diff = abs(row.get('steering_diff', 0))
        throttle_brake = row.get('throttle_brake_overlap', 0)

        # Classification logic
        if brake_diff > 30:
            return 'sudden_braking'
        elif throttle_diff > 40:
            return 'erratic_throttle'
        elif steering_diff > 20:
            return 'steering_correction'
        elif throttle_brake > 20:
            return 'throttle_brake_overlap'
        elif speed_diff > 20:
            return 'speed_anomaly'
        else:
            return 'general_anomaly'

    def _explain_anomaly(self, row: pd.Series, anomaly_type: str) -> str:
        """Generate human-readable explanation for anomaly."""
        explanations = {
            'sudden_braking': f"Sudden braking detected (brake change: {abs(row.get('brake_diff', 0)):.1f}). Possible late braking or unexpected obstacle.",
            'erratic_throttle': f"Erratic throttle application (change: {abs(row.get('throttle_diff', 0)):.1f}%). Check throttle consistency.",
            'steering_correction': f"Large steering correction ({abs(row.get('steering_diff', 0)):.1f}°). Possible oversteer/understeer recovery.",
            'throttle_brake_overlap': f"Simultaneous throttle and brake detected. May indicate left-foot braking or potential issue.",
            'speed_anomaly': f"Unusual speed change ({abs(row.get('speed_diff', 0)):.1f} km/h). Check for wheel spin or lock-up.",
            'general_anomaly': "Unusual driving pattern detected. Review this section of the lap."
        }
        return explanations.get(anomaly_type, "Unknown anomaly detected.")

    def save(self, path: str):
        """Save the fitted model to disk."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Nothing to save.")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {path}")

    def load(self, path: str):
        """Load a fitted model from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_fitted = True
        print(f"Model loaded from {path}")


def train_anomaly_detector(telemetry_df: pd.DataFrame, laps: Optional[List[int]] = None) -> DrivingAnomalyDetector:
    """
    Train an anomaly detector on multiple laps of telemetry data.

    Args:
        telemetry_df: Full telemetry DataFrame
        laps: List of lap numbers to use for training (None = all laps)

    Returns:
        Fitted DrivingAnomalyDetector
    """
    if laps is None:
        laps = telemetry_df['lap'].unique().tolist()

    # Combine data from multiple laps
    training_data = []
    for lap in laps:
        lap_data = telemetry_df[telemetry_df['lap'] == lap].copy()
        if len(lap_data) > 100:  # Skip very short laps
            training_data.append(lap_data)

    if not training_data:
        raise ValueError("No valid training data found")

    combined_df = pd.concat(training_data, ignore_index=True)

    # Train detector
    detector = DrivingAnomalyDetector(contamination=0.03)  # 3% anomaly rate
    detector.fit(combined_df)

    return detector
