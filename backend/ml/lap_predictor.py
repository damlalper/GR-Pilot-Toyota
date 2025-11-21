"""
Lap Time Prediction Model for GR-Pilot
Uses XGBoost to predict lap times based on telemetry features.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    from sklearn.ensemble import GradientBoostingRegressor

from typing import Dict, List, Tuple, Optional
from .feature_engineering import LapFeatureAggregator, create_training_dataset


class LapTimePredictor:
    """
    Predicts lap times based on driving style and telemetry features.
    Can be used to:
    - Estimate potential lap time from partial data
    - Compare predicted vs actual (find improvement areas)
    - Understand which factors most affect lap time
    """

    def __init__(self):
        if HAS_XGBOOST:
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )

        self.scaler = StandardScaler()
        self.aggregator = LapFeatureAggregator()
        self.is_fitted = False
        self.feature_names = []
        self.feature_importance = {}

    def _get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """Get feature columns (exclude lap, lap_time, and non-numeric)."""
        exclude_cols = ['lap', 'lap_time', 'timestamp']
        feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]
        return feature_cols

    def fit(self, training_df: pd.DataFrame) -> 'LapTimePredictor':
        """
        Fit the lap time predictor on training data.

        Args:
            training_df: DataFrame with lap-level features and 'lap_time' column
        """
        if 'lap_time' not in training_df.columns:
            raise ValueError("Training data must have 'lap_time' column")

        # Get features
        self.feature_names = self._get_feature_columns(training_df)
        X = training_df[self.feature_names].fillna(0).values
        y = training_df['lap_time'].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled, y)
        self.is_fitted = True

        # Get feature importance
        if HAS_XGBOOST:
            importances = self.model.feature_importances_
        else:
            importances = self.model.feature_importances_

        self.feature_importance = dict(zip(self.feature_names, importances))
        self.feature_importance = dict(sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True))

        print(f"Lap time predictor fitted on {len(X)} laps with {len(self.feature_names)} features")
        return self

    def predict(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Predict lap times from features.

        Args:
            features_df: DataFrame with same features as training

        Returns:
            Array of predicted lap times
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X = features_df[self.feature_names].fillna(0).values
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return predictions

    def predict_from_telemetry(self, telemetry_df: pd.DataFrame) -> float:
        """
        Predict lap time directly from raw telemetry data.

        Args:
            telemetry_df: Raw telemetry DataFrame for a single lap

        Returns:
            Predicted lap time in seconds
        """
        # Aggregate features
        features = self.aggregator.aggregate_lap_features(telemetry_df)
        features_df = pd.DataFrame([features])

        # Ensure all required features exist
        for col in self.feature_names:
            if col not in features_df.columns:
                features_df[col] = 0

        return self.predict(features_df)[0]

    def evaluate(self, test_df: pd.DataFrame) -> Dict:
        """
        Evaluate model performance on test data.

        Args:
            test_df: Test DataFrame with features and lap_time

        Returns:
            Dictionary with evaluation metrics
        """
        y_true = test_df['lap_time'].values
        y_pred = self.predict(test_df)

        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'predictions': y_pred.tolist(),
            'actual': y_true.tolist()
        }

    def get_improvement_suggestions(self, telemetry_df: pd.DataFrame) -> List[Dict]:
        """
        Analyze telemetry and suggest improvements based on feature importance.

        Args:
            telemetry_df: Raw telemetry for a lap

        Returns:
            List of improvement suggestions
        """
        features = self.aggregator.aggregate_lap_features(telemetry_df)
        suggestions = []

        # Get top important features
        top_features = list(self.feature_importance.items())[:10]

        for feature, importance in top_features:
            if feature in features:
                value = features[feature]
                suggestion = self._generate_suggestion(feature, value, importance)
                if suggestion:
                    suggestions.append(suggestion)

        return suggestions

    def _generate_suggestion(self, feature: str, value: float, importance: float) -> Optional[Dict]:
        """Generate suggestion based on feature value."""
        suggestion = None

        if feature == 'full_throttle_pct' and value < 40:
            suggestion = {
                'feature': feature,
                'current_value': value,
                'importance': importance,
                'title': 'Increase Full Throttle Usage',
                'description': f"Full throttle is only {value:.1f}% of the lap. More aggressive throttle application on straights could improve lap time.",
                'priority': 'high' if importance > 0.1 else 'medium'
            }
        elif feature == 'braking_pct' and value > 15:
            suggestion = {
                'feature': feature,
                'current_value': value,
                'importance': importance,
                'title': 'Reduce Braking Time',
                'description': f"Braking covers {value:.1f}% of the lap. Later braking points or trail braking could save time.",
                'priority': 'high' if importance > 0.1 else 'medium'
            }
        elif feature == 'steering_corrections' and value > 50:
            suggestion = {
                'feature': feature,
                'current_value': value,
                'importance': importance,
                'title': 'Smoother Steering',
                'description': f"High number of steering corrections ({int(value)}). Smoother inputs could improve consistency and speed.",
                'priority': 'medium'
            }
        elif feature == 'speed_std' and value > 30:
            suggestion = {
                'feature': feature,
                'current_value': value,
                'importance': importance,
                'title': 'Speed Consistency',
                'description': f"High speed variation (std: {value:.1f}). More consistent speed through corners may help.",
                'priority': 'medium'
            }

        return suggestion

    def save(self, path: str):
        """Save the fitted model to disk."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Nothing to save.")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance
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
        self.feature_importance = model_data['feature_importance']
        self.is_fitted = True
        print(f"Model loaded from {path}")


def train_lap_predictor(telemetry_df: pd.DataFrame, laps: Optional[List[int]] = None) -> Tuple[LapTimePredictor, Dict]:
    """
    Train a lap time predictor on telemetry data.

    Args:
        telemetry_df: Full telemetry DataFrame with 'lap' column
        laps: List of lap numbers to use (None = all)

    Returns:
        Tuple of (fitted predictor, evaluation metrics)
    """
    if laps is None:
        laps = telemetry_df['lap'].unique().tolist()

    # Create training dataset
    training_df = create_training_dataset(telemetry_df, laps)

    if len(training_df) < 5:
        raise ValueError("Need at least 5 laps to train predictor")

    # Split data
    train_df, test_df = train_test_split(training_df, test_size=0.2, random_state=42)

    # Train predictor
    predictor = LapTimePredictor()
    predictor.fit(train_df)

    # Evaluate
    metrics = predictor.evaluate(test_df)

    print(f"Lap Time Predictor trained: MAE={metrics['mae']:.2f}s, R2={metrics['r2']:.3f}")

    return predictor, metrics
