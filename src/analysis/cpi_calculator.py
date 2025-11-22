"""
Composite Performance Index (CPI) Calculator
Toyota mühendisleri için tek bir performans metriği (0-100)

CPI = w1·Speed + w2·Brake + w3·Throttle + w4·Tire + w5·Turn + w6·Consistency
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CompositePerformanceIndex:
    """
    Toyota mühendisleri için tek bir performans metriği (0-100).

    CPI Formula:
    CPI = w1·Speed + w2·Brake + w3·Throttle + w4·Tire + w5·Turn + w6·Consistency

    Ağırlıklar (toplam=1.0):
    - Speed Score: 0.25
    - Brake Efficiency: 0.20
    - Throttle Smoothness: 0.15
    - Tire Stress (inverted): 0.15
    - Turn Entry Quality: 0.15
    - Consistency: 0.10
    """

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        Initialize CPI calculator

        Args:
            custom_weights: Özel ağırlıklar (opsiyonel)
        """
        self.weights = {
            'speed': 0.25,
            'brake': 0.20,
            'throttle': 0.15,
            'tire': 0.15,
            'turn': 0.15,
            'consistency': 0.10
        }

        if custom_weights:
            self.weights.update(custom_weights)

        # Ağırlıkların toplamı 1.0 olmalı
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total_weight}, normalizing...")
            self.weights = {k: v/total_weight for k, v in self.weights.items()}

    def calculate_speed_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Hız skoru: Ortalama hızın teorik maksimuma oranı

        Args:
            df: DataFrame
            lap_num: Tur numarası (None ise tüm veri)

        Returns:
            Speed score (0-100)
        """
        if 'Speed' not in df.columns:
            logger.warning("Speed column not found, returning neutral score")
            return 50.0

        if lap_num is not None and 'LapNumber' in df.columns:
            lap_data = df[df['LapNumber'] == lap_num]
        else:
            lap_data = df

        if len(lap_data) == 0:
            return 50.0

        avg_speed = lap_data['Speed'].mean()
        max_possible_speed = df['Speed'].quantile(0.95)  # Top %5 hız

        if max_possible_speed == 0:
            return 50.0

        speed_score = (avg_speed / max_possible_speed) * 100
        return min(speed_score, 100.0)

    def calculate_brake_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Fren skoru: Brake efficiency'nin optimize edilmiş değeri

        Args:
            df: DataFrame
            lap_num: Tur numarası

        Returns:
            Brake score (0-100)
        """
        if 'BrakePressure' not in df.columns:
            logger.warning("BrakePressure column not found, returning neutral score")
            return 50.0

        if lap_num is not None and 'LapNumber' in df.columns:
            lap_data = df[df['LapNumber'] == lap_num]
        else:
            lap_data = df

        if len(lap_data) == 0:
            return 50.0

        # Fren basıncı > 0 olan noktalar
        braking_points = lap_data[lap_data['BrakePressure'] > 0]

        if len(braking_points) == 0:
            return 50.0  # Neutral score

        # İdeal fren basıncı: 70-90 bar arası
        ideal_brake_pressure = 80.0
        brake_deviation = abs(braking_points['BrakePressure'] - ideal_brake_pressure).mean()

        brake_score = 100 - (brake_deviation / ideal_brake_pressure * 100)
        return max(brake_score, 0.0)

    def calculate_throttle_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Gaz skoru: Throttle smoothness metriği

        Args:
            df: DataFrame
            lap_num: Tur numarası

        Returns:
            Throttle score (0-100)
        """
        if 'throttle_smoothness' in df.columns:
            if lap_num is not None and 'LapNumber' in df.columns:
                lap_data = df[df['LapNumber'] == lap_num]
            else:
                lap_data = df

            if len(lap_data) == 0:
                return 50.0

            return lap_data['throttle_smoothness'].mean()

        elif 'Throttle' in df.columns:
            # throttle_smoothness feature yoksa manuel hesapla
            if lap_num is not None and 'LapNumber' in df.columns:
                lap_data = df[df['LapNumber'] == lap_num]
            else:
                lap_data = df

            if len(lap_data) == 0:
                return 50.0

            throttle_change = lap_data['Throttle'].diff().abs()
            smoothness = 100 - (throttle_change.mean() * 100)
            return max(min(smoothness, 100.0), 0.0)

        else:
            logger.warning("Throttle column not found, returning neutral score")
            return 50.0

    def calculate_tire_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Lastik skoru: Tire stress'in tersi (düşük stress = yüksek skor)

        Args:
            df: DataFrame
            lap_num: Tur numarası

        Returns:
            Tire score (0-100)
        """
        if 'tire_stress' not in df.columns:
            logger.warning("tire_stress column not found, returning neutral score")
            return 50.0

        if lap_num is not None and 'LapNumber' in df.columns:
            lap_data = df[df['LapNumber'] == lap_num]
        else:
            lap_data = df

        if len(lap_data) == 0:
            return 50.0

        avg_tire_stress = lap_data['tire_stress'].mean()

        # Stress'i tersine çevir (düşük stress = iyi)
        tire_score = 100 - avg_tire_stress
        return max(tire_score, 0.0)

    def calculate_turn_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Viraj skoru: Turn entry quality ortalaması

        Args:
            df: DataFrame
            lap_num: Tur numarası

        Returns:
            Turn score (0-100)
        """
        if 'turn_entry_quality' not in df.columns:
            logger.warning("turn_entry_quality column not found, returning neutral score")
            return 50.0

        if lap_num is not None and 'LapNumber' in df.columns:
            lap_data = df[df['LapNumber'] == lap_num]
        else:
            lap_data = df

        if len(lap_data) == 0:
            return 50.0

        return lap_data['turn_entry_quality'].mean()

    def calculate_consistency_score(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> float:
        """
        Tutarlılık skoru: Speed consistency metriği

        Args:
            df: DataFrame
            lap_num: Tur numarası

        Returns:
            Consistency score (0-100)
        """
        if 'speed_consistency' not in df.columns:
            logger.warning("speed_consistency column not found, returning neutral score")
            return 50.0

        if lap_num is not None and 'LapNumber' in df.columns:
            lap_data = df[df['LapNumber'] == lap_num]
        else:
            lap_data = df

        if len(lap_data) == 0:
            return 50.0

        return lap_data['speed_consistency'].mean()

    def calculate_cpi(self, df: pd.DataFrame, lap_num: Optional[int] = None) -> Dict:
        """
        Ana CPI hesaplaması

        Args:
            df: DataFrame (feature-engineered olmalı)
            lap_num: Tur numarası (None ise tüm veri)

        Returns:
            Dict: {
                'total_cpi': float,
                'breakdown': {...},
                'weighted_contributions': {...},
                'interpretation': str
            }
        """
        # Her bir component'i hesapla
        scores = {
            'speed': self.calculate_speed_score(df, lap_num),
            'brake': self.calculate_brake_score(df, lap_num),
            'throttle': self.calculate_throttle_score(df, lap_num),
            'tire': self.calculate_tire_score(df, lap_num),
            'turn': self.calculate_turn_score(df, lap_num),
            'consistency': self.calculate_consistency_score(df, lap_num)
        }

        # Ağırlıklı toplam
        total_cpi = sum(
            scores[key] * self.weights[key]
            for key in scores.keys()
        )

        # Weighted contributions
        weighted_contributions = {
            key: scores[key] * self.weights[key]
            for key in scores.keys()
        }

        result = {
            'total_cpi': round(total_cpi, 1),
            'breakdown': {
                'Speed Score': round(scores['speed'], 1),
                'Brake Efficiency': round(scores['brake'], 1),
                'Throttle Smoothness': round(scores['throttle'], 1),
                'Tire Management': round(scores['tire'], 1),
                'Turn Entry Quality': round(scores['turn'], 1),
                'Consistency': round(scores['consistency'], 1)
            },
            'weighted_contributions': {
                key.replace('_', ' ').title(): round(val, 2)
                for key, val in weighted_contributions.items()
            },
            'interpretation': self.get_cpi_interpretation(total_cpi),
            'grade': self.get_cpi_grade(total_cpi)
        }

        logger.info(f"CPI calculated: {total_cpi:.1f}/100 (Lap {lap_num if lap_num else 'All'})")

        return result

    def get_cpi_interpretation(self, cpi: float) -> str:
        """
        CPI skoruna göre yorum

        Args:
            cpi: CPI score (0-100)

        Returns:
            Interpretation string
        """
        if cpi >= 90:
            return "Excellent - Near-perfect lap execution"
        elif cpi >= 80:
            return "Good - Solid performance, minor improvements possible"
        elif cpi >= 70:
            return "Average - Several areas need attention"
        elif cpi >= 60:
            return "Below Average - Significant issues detected"
        else:
            return "Poor - Critical performance problems"

    def get_cpi_grade(self, cpi: float) -> str:
        """
        CPI grade (A, B, C, D, F)

        Args:
            cpi: CPI score

        Returns:
            Grade letter
        """
        if cpi >= 90:
            return "A"
        elif cpi >= 80:
            return "B"
        elif cpi >= 70:
            return "C"
        elif cpi >= 60:
            return "D"
        else:
            return "F"

    def calculate_all_laps(self, df: pd.DataFrame) -> Dict[int, Dict]:
        """
        Tüm turlar için CPI hesapla

        Args:
            df: DataFrame

        Returns:
            Dict of lap CPI results
        """
        if 'LapNumber' not in df.columns:
            logger.warning("LapNumber column not found, calculating for entire dataset")
            return {0: self.calculate_cpi(df)}

        lap_cpis = {}

        for lap_num in sorted(df['LapNumber'].unique()):
            lap_cpis[int(lap_num)] = self.calculate_cpi(df, lap_num)

        logger.info(f"Calculated CPI for {len(lap_cpis)} laps")

        return lap_cpis

    def get_best_lap(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """
        En iyi CPI'ye sahip turu bul

        Args:
            df: DataFrame

        Returns:
            (lap_number, cpi_result)
        """
        all_laps = self.calculate_all_laps(df)

        if not all_laps:
            return (0, {})

        best_lap = max(all_laps.items(), key=lambda x: x[1]['total_cpi'])

        logger.info(f"Best lap: {best_lap[0]} with CPI {best_lap[1]['total_cpi']}")

        return best_lap

    def get_worst_lap(self, df: pd.DataFrame) -> Tuple[int, Dict]:
        """
        En kötü CPI'ye sahip turu bul

        Args:
            df: DataFrame

        Returns:
            (lap_number, cpi_result)
        """
        all_laps = self.calculate_all_laps(df)

        if not all_laps:
            return (0, {})

        worst_lap = min(all_laps.items(), key=lambda x: x[1]['total_cpi'])

        logger.info(f"Worst lap: {worst_lap[0]} with CPI {worst_lap[1]['total_cpi']}")

        return worst_lap


# Örnek kullanım
if __name__ == "__main__":
    # Test data
    test_df = pd.DataFrame({
        'LapNumber': np.repeat(range(1, 6), 100),
        'Speed': np.random.normal(150, 20, 500),
        'BrakePressure': np.random.uniform(0, 100, 500),
        'Throttle': np.random.uniform(0, 100, 500),
        'throttle_smoothness': np.random.uniform(70, 95, 500),
        'tire_stress': np.random.uniform(20, 60, 500),
        'turn_entry_quality': np.random.uniform(60, 90, 500),
        'speed_consistency': np.random.uniform(75, 95, 500)
    })

    # CPI Calculator
    cpi_calc = CompositePerformanceIndex()

    # Tek tur için
    lap_1_cpi = cpi_calc.calculate_cpi(test_df, lap_num=1)
    print(f"\nLap 1 CPI: {lap_1_cpi['total_cpi']}/100")
    print(f"Grade: {lap_1_cpi['grade']}")
    print(f"Interpretation: {lap_1_cpi['interpretation']}")
    print(f"Breakdown: {lap_1_cpi['breakdown']}")

    # Tüm turlar için
    all_laps = cpi_calc.calculate_all_laps(test_df)
    print(f"\nAll Laps CPI:")
    for lap, result in all_laps.items():
        print(f"  Lap {lap}: {result['total_cpi']}/100 ({result['grade']})")

    # En iyi/en kötü tur
    best_lap, best_result = cpi_calc.get_best_lap(test_df)
    worst_lap, worst_result = cpi_calc.get_worst_lap(test_df)
    print(f"\nBest Lap: {best_lap} (CPI: {best_result['total_cpi']})")
    print(f"Worst Lap: {worst_lap} (CPI: {worst_result['total_cpi']})")
