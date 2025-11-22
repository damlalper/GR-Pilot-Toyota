"""
Grip Index Calculator
Weather + Telemetry → Track Grip Estimation

GERÇEK TOYOTA MÜHENDİSLİK:
Track temp, tire temp, humidity → Grip coefficient (0-100)
Tire degradation prediction
Optimal tire pressure recommendation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GripIndexCalculator:
    """
    Track grip seviyesi hesaplayıcı

    Physics-based model:
    - Track temperature (optimal: 25-35°C)
    - Tire temperature (optimal: 80-100°C)
    - Humidity (lower = better grip)
    - Tire degradation over laps
    - Rainfall (catastrophic grip loss)
    """

    def __init__(self):
        self.grip_history: pd.DataFrame = pd.DataFrame()
        self.optimal_track_temp = 30.0  # °C
        self.optimal_tire_temp = 90.0   # °C

    def calculate_temperature_factor(
        self,
        track_temp: float,
        tire_temp: Optional[float] = None
    ) -> float:
        """
        Sıcaklık faktörü (0-1)

        Track temp curve:
        - <10°C: Poor grip (0.5)
        - 25-35°C: Optimal (1.0)
        - >50°C: Degraded grip (0.6)

        Args:
            track_temp: Track surface temperature (°C)
            tire_temp: Tire temperature (°C, optional)

        Returns:
            Temperature factor (0-1)
        """
        # Track temperature factor
        if track_temp < 10:
            track_factor = 0.5
        elif 25 <= track_temp <= 35:
            track_factor = 1.0
        elif track_temp > 50:
            track_factor = 0.6
        else:
            # Linear interpolation
            if track_temp < 25:
                track_factor = 0.5 + (track_temp - 10) / 15 * 0.5
            else:
                track_factor = 1.0 - (track_temp - 35) / 15 * 0.4

        # Tire temperature factor (if available)
        if tire_temp is not None:
            if tire_temp < 60:
                tire_factor = 0.6 + (tire_temp - 40) / 20 * 0.2
            elif 80 <= tire_temp <= 100:
                tire_factor = 1.0
            elif tire_temp > 120:
                tire_factor = 0.5
            else:
                if tire_temp < 80:
                    tire_factor = 0.8 + (tire_temp - 60) / 20 * 0.2
                else:
                    tire_factor = 1.0 - (tire_temp - 100) / 20 * 0.5

            # Combined factor
            return (track_factor * 0.6 + tire_factor * 0.4)

        return track_factor

    def calculate_humidity_factor(self, humidity: float) -> float:
        """
        Nem faktörü (0-1)

        Lower humidity = better grip
        - 0-30%: Excellent (1.0)
        - 30-60%: Good (0.9)
        - 60-80%: Fair (0.7)
        - >80%: Poor (0.5)

        Args:
            humidity: Relative humidity (%)

        Returns:
            Humidity factor (0-1)
        """
        if humidity < 30:
            return 1.0
        elif humidity < 60:
            return 0.9 - (humidity - 30) / 30 * 0.2
        elif humidity < 80:
            return 0.7 - (humidity - 60) / 20 * 0.2
        else:
            return 0.5

    def calculate_tire_degradation_factor(
        self,
        lap_number: int,
        tire_compound: str = "medium",
        stint_length: int = 20
    ) -> float:
        """
        Lastik degradation faktörü

        Gerçek fizik:
        - Soft: Fast degradation (5% per lap)
        - Medium: Moderate (3% per lap)
        - Hard: Slow (2% per lap)

        Args:
            lap_number: Current lap in stint
            tire_compound: "soft", "medium", "hard"
            stint_length: Expected stint length

        Returns:
            Degradation factor (0-1)
        """
        degradation_rates = {
            "soft": 0.05,
            "medium": 0.03,
            "hard": 0.02
        }

        rate = degradation_rates.get(tire_compound.lower(), 0.03)

        # Linear degradation model
        degradation = 1.0 - (lap_number * rate)

        # Cliff effect (rapid dropoff near end)
        if lap_number > stint_length * 0.8:
            cliff_factor = (lap_number - stint_length * 0.8) / (stint_length * 0.2)
            degradation *= (1.0 - cliff_factor * 0.3)

        return max(0.3, degradation)  # Never below 30% grip

    def calculate_surface_condition_factor(
        self,
        rainfall: float = 0.0,
        track_wetness: float = 0.0
    ) -> float:
        """
        Pist yüzey durumu

        Args:
            rainfall: Rain intensity (mm/h, 0-50)
            track_wetness: Track wetness (%, 0-100)

        Returns:
            Surface factor (0-1)
        """
        # Dry track
        if rainfall == 0 and track_wetness == 0:
            return 1.0

        # Light rain
        elif rainfall < 5:
            return 0.7 - (rainfall / 5 * 0.2)

        # Moderate rain
        elif rainfall < 15:
            return 0.5 - ((rainfall - 5) / 10 * 0.2)

        # Heavy rain
        else:
            return 0.3

    def calculate_grip_index(
        self,
        track_temp: float,
        humidity: float,
        lap_number: int = 1,
        tire_temp: Optional[float] = None,
        tire_compound: str = "medium",
        rainfall: float = 0.0,
        track_wetness: float = 0.0
    ) -> float:
        """
        Master grip index calculator (0-100)

        Formula:
        Grip = (temp_factor × humidity_factor × degradation_factor × surface_factor) × 100

        Args:
            track_temp: Track temperature (°C)
            humidity: Relative humidity (%)
            lap_number: Current lap number
            tire_temp: Tire temperature (°C, optional)
            tire_compound: Tire type
            rainfall: Rain intensity
            track_wetness: Track wetness percentage

        Returns:
            Grip index (0-100)
        """
        temp_factor = self.calculate_temperature_factor(track_temp, tire_temp)
        humidity_factor = self.calculate_humidity_factor(humidity)
        degradation_factor = self.calculate_tire_degradation_factor(
            lap_number, tire_compound
        )
        surface_factor = self.calculate_surface_condition_factor(
            rainfall, track_wetness
        )

        # Weighted combination
        grip_index = (
            temp_factor * 0.35 +
            humidity_factor * 0.20 +
            degradation_factor * 0.30 +
            surface_factor * 0.15
        ) * 100

        return float(min(100, max(0, grip_index)))

    def analyze_grip_over_session(
        self,
        weather_df: pd.DataFrame,
        telemetry_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Tüm session boyunca grip analizi

        Args:
            weather_df: Weather data with TrackTemp, Humidity
            telemetry_df: Telemetry with LapNumber

        Returns:
            DataFrame with grip_index per lap
        """
        if 'LapNumber' not in telemetry_df.columns:
            logger.error("LapNumber column required")
            return pd.DataFrame()

        grip_data = []

        for lap in telemetry_df['LapNumber'].unique():
            lap_data = telemetry_df[telemetry_df['LapNumber'] == lap]

            # Get weather data for this lap
            if 'TrackTemp' in weather_df.columns:
                track_temp = weather_df['TrackTemp'].iloc[0] if len(weather_df) > 0 else 25.0
            else:
                track_temp = 25.0

            if 'Humidity' in weather_df.columns:
                humidity = weather_df['Humidity'].iloc[0] if len(weather_df) > 0 else 50.0
            else:
                humidity = 50.0

            # Calculate grip
            grip = self.calculate_grip_index(
                track_temp=track_temp,
                humidity=humidity,
                lap_number=int(lap)
            )

            grip_data.append({
                'LapNumber': int(lap),
                'grip_index': grip,
                'track_temp': track_temp,
                'humidity': humidity
            })

        self.grip_history = pd.DataFrame(grip_data)
        logger.info(f"Analyzed grip for {len(grip_data)} laps")

        return self.grip_history

    def predict_optimal_pit_window(
        self,
        current_lap: int,
        tire_compound: str = "medium",
        target_grip_threshold: float = 60.0
    ) -> Dict:
        """
        Optimal pit window prediction

        Grip threshold altına düşmeden önce pit yapılmalı

        Args:
            current_lap: Current lap number
            tire_compound: Current tire compound
            target_grip_threshold: Minimum acceptable grip

        Returns:
            Dict with pit recommendation
        """
        # Simulate grip degradation
        laps_ahead = []
        for future_lap in range(current_lap, current_lap + 30):
            degradation = self.calculate_tire_degradation_factor(
                future_lap - current_lap + 1,
                tire_compound
            )

            # Assume constant conditions
            estimated_grip = degradation * 85  # Base grip 85

            laps_ahead.append({
                'lap': future_lap,
                'estimated_grip': estimated_grip
            })

            if estimated_grip < target_grip_threshold:
                break

        # Find optimal window
        optimal_pit_lap = None
        for lap_data in laps_ahead:
            if lap_data['estimated_grip'] < target_grip_threshold:
                optimal_pit_lap = lap_data['lap'] - 2  # Pit 2 laps before threshold
                break

        return {
            'current_lap': current_lap,
            'optimal_pit_lap': optimal_pit_lap,
            'laps_remaining': optimal_pit_lap - current_lap if optimal_pit_lap else None,
            'current_estimated_grip': laps_ahead[0]['estimated_grip'] if laps_ahead else None,
            'tire_compound': tire_compound,
            'recommendation': self._generate_pit_recommendation(
                current_lap, optimal_pit_lap, tire_compound
            )
        }

    def _generate_pit_recommendation(
        self,
        current_lap: int,
        optimal_pit_lap: Optional[int],
        tire_compound: str
    ) -> str:
        """Generate pit strategy recommendation text"""
        if optimal_pit_lap is None:
            return f"Tires still good. Continue on {tire_compound} compound."

        laps_to_pit = optimal_pit_lap - current_lap

        if laps_to_pit <= 2:
            return f"⚠️ PIT NOW! Grip degrading rapidly. Switch from {tire_compound}."
        elif laps_to_pit <= 5:
            return f"⏰ Pit window opening in {laps_to_pit} laps. Prepare for tire change."
        else:
            return f"✅ Tires healthy. Optimal pit in ~{laps_to_pit} laps."

    def calculate_tire_pressure_recommendation(
        self,
        track_temp: float,
        tire_temp: Optional[float] = None
    ) -> Dict:
        """
        Optimal tire pressure recommendation

        Gerçek fizik:
        - Cold track: +1 PSI
        - Hot track: -1 PSI
        - Base pressure: 27 PSI (F1 standard)

        Args:
            track_temp: Track temperature
            tire_temp: Tire temperature

        Returns:
            Dict with pressure recommendations
        """
        base_pressure = 27.0  # PSI

        # Track temp adjustment
        if track_temp < 20:
            adjustment = +1.5
        elif track_temp > 40:
            adjustment = -1.0
        else:
            adjustment = (30 - track_temp) / 10 * 0.5

        recommended_pressure = base_pressure + adjustment

        return {
            'front_left': round(recommended_pressure, 1),
            'front_right': round(recommended_pressure, 1),
            'rear_left': round(recommended_pressure - 0.5, 1),  # Slightly lower rear
            'rear_right': round(recommended_pressure - 0.5, 1),
            'track_temp': track_temp,
            'adjustment': f"{adjustment:+.1f} PSI vs base"
        }


# Test
if __name__ == "__main__":
    calc = GripIndexCalculator()

    # Test 1: Single grip calculation
    print("=== GRIP INDEX TEST ===")
    grip = calc.calculate_grip_index(
        track_temp=28.0,
        humidity=45.0,
        lap_number=5,
        tire_compound="medium"
    )
    print(f"Grip Index: {grip:.1f}/100")

    # Test 2: Pit window prediction
    print("\n=== PIT STRATEGY ===")
    pit_rec = calc.predict_optimal_pit_window(
        current_lap=12,
        tire_compound="soft"
    )
    print(f"Current Lap: {pit_rec['current_lap']}")
    print(f"Optimal Pit Lap: {pit_rec['optimal_pit_lap']}")
    print(f"Recommendation: {pit_rec['recommendation']}")

    # Test 3: Tire pressure
    print("\n=== TIRE PRESSURE ===")
    pressure = calc.calculate_tire_pressure_recommendation(track_temp=32.0)
    print(f"FL: {pressure['front_left']} PSI")
    print(f"FR: {pressure['front_right']} PSI")
    print(f"RL: {pressure['rear_left']} PSI")
    print(f"RR: {pressure['rear_right']} PSI")
    print(f"Adjustment: {pressure['adjustment']}")
