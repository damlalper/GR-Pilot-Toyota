"""
Driver Style Clustering for GR-Pilot
Uses K-Means to identify different driving styles and create Driver DNA profiles.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Optional
import pickle
import os

from .feature_engineering import LapFeatureAggregator


class DriverStyleClusterer:
    """
    Clusters driving styles into distinct profiles using K-Means.
    Creates a "Driver DNA" fingerprint for each lap/driver.
    """

    STYLE_NAMES = {
        0: 'Aggressive Attacker',
        1: 'Smooth Operator',
        2: 'Balanced Racer',
        3: 'Conservative Driver',
        4: 'Inconsistent Learner'
    }

    STYLE_DESCRIPTIONS = {
        'Aggressive Attacker': 'High risk, high reward. Late braking, aggressive throttle, pushes limits.',
        'Smooth Operator': 'Consistent and precise. Prioritizes tire preservation and clean racing.',
        'Balanced Racer': 'Good mix of speed and consistency. Adaptable to conditions.',
        'Conservative Driver': 'Safe approach with room for improvement. Good foundation.',
        'Inconsistent Learner': 'Variable patterns. Still developing technique.'
    }

    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)  # For visualization
        self.aggregator = LapFeatureAggregator()
        self.is_fitted = False
        self.feature_names = []
        self.cluster_centers = None
        self.cluster_profiles = {}

    def _get_style_features(self, df: pd.DataFrame) -> List[str]:
        """Get features relevant for style classification."""
        style_features = [
            'throttle_mean', 'throttle_std', 'full_throttle_pct', 'lift_off_pct',
            'brake_mean', 'brake_max', 'braking_pct', 'hard_braking_pct',
            'steering_mean_abs', 'steering_std', 'steering_corrections',
            'speed_std', 'speed_mean', 'speed_max'
        ]
        return [f for f in style_features if f in df.columns]

    def fit(self, training_df: pd.DataFrame) -> 'DriverStyleClusterer':
        """
        Fit the clusterer on training data.

        Args:
            training_df: DataFrame with lap-level features
        """
        self.feature_names = self._get_style_features(training_df)

        if len(self.feature_names) < 3:
            raise ValueError("Not enough features for clustering")

        X = training_df[self.feature_names].fillna(0).values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit K-Means
        self.kmeans.fit(X_scaled)
        self.is_fitted = True

        # Get cluster centers in original scale
        self.cluster_centers = self.scaler.inverse_transform(self.kmeans.cluster_centers_)

        # Fit PCA for visualization
        self.pca.fit(X_scaled)

        # Analyze clusters to create profiles
        self._analyze_clusters(training_df, X_scaled)

        print(f"Driver style clusterer fitted with {self.n_clusters} clusters on {len(X)} samples")
        return self

    def _analyze_clusters(self, df: pd.DataFrame, X_scaled: np.ndarray):
        """Analyze cluster characteristics to create profiles."""
        labels = self.kmeans.labels_

        for cluster_id in range(self.n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = df[cluster_mask]

            if len(cluster_data) == 0:
                continue

            profile = {
                'cluster_id': cluster_id,
                'style_name': self.STYLE_NAMES.get(cluster_id, f'Style {cluster_id}'),
                'sample_count': len(cluster_data),
                'characteristics': {}
            }

            # Calculate average characteristics
            for feature in self.feature_names:
                if feature in cluster_data.columns:
                    profile['characteristics'][feature] = float(cluster_data[feature].mean())

            # Determine style based on characteristics
            profile['style_name'] = self._determine_style(profile['characteristics'])
            profile['description'] = self.STYLE_DESCRIPTIONS.get(profile['style_name'], '')

            self.cluster_profiles[cluster_id] = profile

    def _determine_style(self, characteristics: Dict) -> str:
        """Determine driving style name based on characteristics."""
        throttle_aggression = characteristics.get('full_throttle_pct', 50)
        brake_intensity = characteristics.get('hard_braking_pct', 10)
        steering_corrections = characteristics.get('steering_corrections', 30)
        speed_consistency = 100 - characteristics.get('speed_std', 30)

        # Classification logic
        if throttle_aggression > 50 and brake_intensity > 15:
            return 'Aggressive Attacker'
        elif speed_consistency > 70 and steering_corrections < 40:
            return 'Smooth Operator'
        elif throttle_aggression > 35 and speed_consistency > 50:
            return 'Balanced Racer'
        elif throttle_aggression < 35 and brake_intensity < 10:
            return 'Conservative Driver'
        else:
            return 'Inconsistent Learner'

    def predict(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster assignments for laps.

        Args:
            features_df: DataFrame with lap-level features

        Returns:
            Array of cluster labels
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X = features_df[self.feature_names].fillna(0).values
        X_scaled = self.scaler.transform(X)
        labels = self.kmeans.predict(X_scaled)
        return labels

    def get_driver_dna(self, telemetry_df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive Driver DNA profile from telemetry.

        Args:
            telemetry_df: Raw telemetry DataFrame for a lap

        Returns:
            Driver DNA profile dictionary
        """
        # Aggregate features
        features = self.aggregator.aggregate_lap_features(telemetry_df)
        features_df = pd.DataFrame([features])

        # Ensure all features exist
        for col in self.feature_names:
            if col not in features_df.columns:
                features_df[col] = 0

        # Get cluster assignment
        if self.is_fitted:
            cluster = self.predict(features_df)[0]
            style_profile = self.cluster_profiles.get(cluster, {})
            style_name = style_profile.get('style_name', 'Unknown')
            style_desc = style_profile.get('description', '')
        else:
            # Fallback without fitted model
            style_name = self._determine_style(features)
            style_desc = self.STYLE_DESCRIPTIONS.get(style_name, '')

        # Calculate DNA scores (0-100)
        dna_scores = self._calculate_dna_scores(features)

        # Generate recommendations
        recommendations = self._generate_recommendations(features, dna_scores)

        return {
            'style_name': style_name,
            'style_description': style_desc,
            'dna_scores': dna_scores,
            'raw_metrics': features,
            'recommendations': recommendations,
            'cluster_id': int(cluster) if self.is_fitted else -1
        }

    def _calculate_dna_scores(self, features: Dict) -> Dict:
        """Calculate normalized DNA scores from features."""
        # Aggression score (0-100)
        throttle_factor = features.get('full_throttle_pct', 50)
        brake_factor = features.get('hard_braking_pct', 10) * 2
        aggression = min((throttle_factor + brake_factor) / 2, 100)

        # Smoothness score (0-100)
        steering_smooth = 100 - min(features.get('steering_corrections', 50) / 2, 100)
        throttle_smooth = 100 - min(features.get('throttle_std', 30), 100)
        smoothness = (steering_smooth + throttle_smooth) / 2

        # Consistency score (0-100)
        speed_consistency = 100 - min(features.get('speed_std', 30), 100)
        consistency = speed_consistency

        # Risk tolerance (0-100)
        speed_risk = min(features.get('speed_max', 150) / 2, 100)
        brake_late = features.get('hard_braking_pct', 10) * 3
        risk_tolerance = min((speed_risk + brake_late) / 2, 100)

        return {
            'aggression': round(aggression, 1),
            'smoothness': round(smoothness, 1),
            'consistency': round(consistency, 1),
            'risk_tolerance': round(risk_tolerance, 1),
            'overall': round((aggression + smoothness + consistency) / 3, 1)
        }

    def _generate_recommendations(self, features: Dict, dna_scores: Dict) -> List[str]:
        """Generate personalized recommendations based on DNA."""
        recommendations = []

        if dna_scores['aggression'] < 40:
            recommendations.append("Try more aggressive throttle application on corner exits")

        if dna_scores['smoothness'] < 50:
            recommendations.append("Focus on smoother steering inputs through corners")

        if dna_scores['consistency'] < 60:
            recommendations.append("Work on maintaining consistent speed through lap sections")

        if features.get('full_throttle_pct', 0) < 30:
            recommendations.append("Increase full throttle usage on straights - currently under-utilizing engine power")

        if features.get('steering_corrections', 0) > 60:
            recommendations.append("Reduce mid-corner steering corrections for better tire preservation")

        if features.get('braking_pct', 0) > 15:
            recommendations.append("Consider later braking points to reduce time spent on brakes")

        # Limit to top 4 recommendations
        return recommendations[:4]

    def get_pca_coordinates(self, features_df: pd.DataFrame) -> np.ndarray:
        """Get 2D PCA coordinates for visualization."""
        if not self.is_fitted:
            raise ValueError("Model not fitted")

        X = features_df[self.feature_names].fillna(0).values
        X_scaled = self.scaler.transform(X)
        return self.pca.transform(X_scaled)

    def save(self, path: str):
        """Save the fitted model to disk."""
        if not self.is_fitted:
            raise ValueError("Model not fitted")

        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'pca': self.pca,
            'feature_names': self.feature_names,
            'cluster_centers': self.cluster_centers,
            'cluster_profiles': self.cluster_profiles,
            'n_clusters': self.n_clusters
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

    def load(self, path: str):
        """Load a fitted model from disk."""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.kmeans = model_data['kmeans']
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.feature_names = model_data['feature_names']
        self.cluster_centers = model_data['cluster_centers']
        self.cluster_profiles = model_data['cluster_profiles']
        self.n_clusters = model_data['n_clusters']
        self.is_fitted = True


def train_driver_clusterer(telemetry_df: pd.DataFrame, laps: Optional[List[int]] = None) -> DriverStyleClusterer:
    """
    Train a driver style clusterer on telemetry data.

    Args:
        telemetry_df: Full telemetry DataFrame
        laps: List of lap numbers to use (None = all)

    Returns:
        Fitted DriverStyleClusterer
    """
    from .feature_engineering import create_training_dataset

    if laps is None:
        laps = telemetry_df['lap'].unique().tolist()

    # Create training dataset
    training_df = create_training_dataset(telemetry_df, laps)

    if len(training_df) < 5:
        raise ValueError("Need at least 5 laps to train clusterer")

    # Train clusterer
    clusterer = DriverStyleClusterer(n_clusters=min(5, len(training_df) // 2))
    clusterer.fit(training_df)

    return clusterer
