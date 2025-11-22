"""
Perfect Lap Reconstruction
Theoretical fastest lap synthesis from best sector performances

GERÇEK F1/ENDURANCE MÜHENDİSLİK:
- Her sektörün en iyi performansını birleştir
- Teorik en hızlı tur hesapla
- Delta visualization vs actual laps
- Track evolution consideration
- Setup consistency validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class PerfectLapReconstructor:
    """
    Teorik mükemmel tur oluşturucu

    F1/WEC teams kullanır:
    - Best sector times → Perfect lap
    - Achievability analysis
    - Delta map generation
    - Improvement potential calculation
    """

    def __init__(self):
        self.best_sectors: Dict[int, Dict] = {}
        self.perfect_lap_data: Optional[pd.DataFrame] = None
        self.theoretical_time: Optional[float] = None

    def identify_best_sectors(
        self,
        telemetry_df: pd.DataFrame,
        sector_column: str = 'Sector',
        lap_column: str = 'LapNumber'
    ) -> Dict[int, Dict]:
        """
        Her sektör için en iyi performansı bul

        Args:
            telemetry_df: Full telemetry with sectors
            sector_column: Sector ID column
            lap_column: Lap number column

        Returns:
            Dict with best sector info per sector
        """
        if sector_column not in telemetry_df.columns:
            logger.error(f"{sector_column} column not found")
            return {}

        if lap_column not in telemetry_df.columns:
            logger.error(f"{lap_column} column not found")
            return {}

        sectors = telemetry_df[sector_column].unique()

        for sector_id in sorted(sectors):
            sector_data = telemetry_df[telemetry_df[sector_column] == sector_id]

            # Group by lap
            laps = sector_data[lap_column].unique()

            best_time = float('inf')
            best_lap = None
            best_data = None

            for lap_num in laps:
                lap_sector_data = sector_data[sector_data[lap_column] == lap_num]

                if len(lap_sector_data) == 0:
                    continue

                # Calculate sector time (using speed integration)
                if 'Speed' in lap_sector_data.columns:
                    # Approximate time: distance / avg speed
                    # Assume constant sampling rate (e.g., 100Hz = 0.01s intervals)
                    avg_speed_ms = lap_sector_data['Speed'].mean() / 3.6  # km/h → m/s

                    if avg_speed_ms > 0:
                        # Rough sector time estimate
                        sector_time = len(lap_sector_data) * 0.01  # 100Hz sampling

                        if sector_time < best_time:
                            best_time = sector_time
                            best_lap = lap_num
                            best_data = lap_sector_data

            if best_data is not None:
                self.best_sectors[int(sector_id)] = {
                    'sector_id': int(sector_id),
                    'best_lap': int(best_lap),
                    'sector_time': round(best_time, 3),
                    'avg_speed': round(best_data['Speed'].mean(), 2) if 'Speed' in best_data.columns else None,
                    'min_speed': round(best_data['Speed'].min(), 2) if 'Speed' in best_data.columns else None,
                    'max_speed': round(best_data['Speed'].max(), 2) if 'Speed' in best_data.columns else None,
                    'data': best_data
                }

        logger.info(f"Identified best sectors: {len(self.best_sectors)}")

        return self.best_sectors

    def calculate_theoretical_lap_time(self) -> float:
        """
        Teorik en hızlı tur zamanı

        Returns:
            Total theoretical time (seconds)
        """
        if not self.best_sectors:
            logger.warning("No best sectors identified")
            return 0.0

        total_time = sum(
            sector['sector_time']
            for sector in self.best_sectors.values()
        )

        self.theoretical_time = round(total_time, 3)

        logger.info(f"Theoretical lap time: {self.theoretical_time}s")

        return self.theoretical_time

    def reconstruct_perfect_lap(self) -> pd.DataFrame:
        """
        Mükemmel tur telemetrisini oluştur

        Her sektörün en iyi telemetrisini birleştir

        Returns:
            DataFrame with perfect lap telemetry
        """
        if not self.best_sectors:
            logger.error("No best sectors to reconstruct from")
            return pd.DataFrame()

        # Combine all sector data
        sector_dfs = []

        for sector_id in sorted(self.best_sectors.keys()):
            sector_info = self.best_sectors[sector_id]
            sector_df = sector_info['data'].copy()

            # Add metadata
            sector_df['perfect_lap_sector'] = sector_id
            sector_df['source_lap'] = sector_info['best_lap']

            sector_dfs.append(sector_df)

        # Concatenate
        self.perfect_lap_data = pd.concat(sector_dfs, ignore_index=True)

        # Add sequential time column
        self.perfect_lap_data['perfect_lap_time'] = np.arange(len(self.perfect_lap_data)) * 0.01  # 100Hz

        logger.info(f"Reconstructed perfect lap: {len(self.perfect_lap_data)} data points")

        return self.perfect_lap_data

    def compare_to_actual_lap(
        self,
        telemetry_df: pd.DataFrame,
        actual_lap_number: int,
        lap_column: str = 'LapNumber'
    ) -> Dict:
        """
        Gerçek tur ile karşılaştırma

        Args:
            telemetry_df: Full telemetry
            actual_lap_number: Lap to compare against
            lap_column: Lap number column

        Returns:
            Dict with comparison metrics
        """
        if self.perfect_lap_data is None:
            logger.error("Perfect lap not reconstructed yet")
            return {}

        # Extract actual lap
        actual_lap = telemetry_df[telemetry_df[lap_column] == actual_lap_number]

        if len(actual_lap) == 0:
            logger.error(f"Lap {actual_lap_number} not found")
            return {}

        # Calculate actual lap time (rough estimate)
        actual_time = len(actual_lap) * 0.01  # 100Hz sampling

        # Time delta
        time_delta = actual_time - self.theoretical_time if self.theoretical_time else 0

        # Speed comparison
        comparison = {
            'actual_lap': actual_lap_number,
            'actual_time': round(actual_time, 3),
            'perfect_time': self.theoretical_time,
            'time_delta': round(time_delta, 3),
            'improvement_pct': round((time_delta / actual_time * 100), 2) if actual_time > 0 else 0
        }

        if 'Speed' in actual_lap.columns and 'Speed' in self.perfect_lap_data.columns:
            comparison['actual_avg_speed'] = round(actual_lap['Speed'].mean(), 2)
            comparison['perfect_avg_speed'] = round(self.perfect_lap_data['Speed'].mean(), 2)
            comparison['speed_delta'] = round(
                comparison['perfect_avg_speed'] - comparison['actual_avg_speed'],
                2
            )

        logger.info(f"Comparison: Actual lap {actual_lap_number} is {time_delta:.3f}s slower than perfect lap")

        return comparison

    def calculate_sector_deltas(
        self,
        telemetry_df: pd.DataFrame,
        actual_lap_number: int,
        sector_column: str = 'Sector',
        lap_column: str = 'LapNumber'
    ) -> List[Dict]:
        """
        Sektör bazlı delta analizi

        Args:
            telemetry_df: Full telemetry
            actual_lap_number: Lap to compare
            sector_column: Sector ID column
            lap_column: Lap number column

        Returns:
            List of sector delta dicts
        """
        deltas = []

        actual_lap = telemetry_df[telemetry_df[lap_column] == actual_lap_number]

        for sector_id, best_info in self.best_sectors.items():
            # Actual sector time
            actual_sector = actual_lap[actual_lap[sector_column] == sector_id]

            if len(actual_sector) == 0:
                continue

            actual_sector_time = len(actual_sector) * 0.01  # 100Hz
            perfect_sector_time = best_info['sector_time']

            delta = actual_sector_time - perfect_sector_time

            deltas.append({
                'sector_id': sector_id,
                'actual_time': round(actual_sector_time, 3),
                'perfect_time': round(perfect_sector_time, 3),
                'delta': round(delta, 3),
                'perfect_from_lap': best_info['best_lap'],
                'status': '🟢 Matched' if delta < 0.05 else ('🟡 Close' if delta < 0.2 else '🔴 Needs Work')
            })

        # Sort by delta (worst first)
        deltas.sort(key=lambda x: x['delta'], reverse=True)

        return deltas

    def check_achievability(self) -> Dict:
        """
        Mükemmel turun gerçekleştirilebilirlik kontrolü

        Farklı turlardan alınan sektörler tutarlı mı?
        (Setup değişimi var mı?)

        Returns:
            Dict with achievability analysis
        """
        if not self.best_sectors:
            return {'achievable': False, 'reason': 'No sectors analyzed'}

        # Check if all sectors from same lap (highly achievable)
        source_laps = [s['best_lap'] for s in self.best_sectors.values()]
        unique_laps = set(source_laps)

        if len(unique_laps) == 1:
            return {
                'achievable': True,
                'confidence': 'Very High',
                'reason': f'All sectors from same lap (Lap {list(unique_laps)[0]})',
                'lap_consistency': 100.0
            }

        # Check lap spread
        lap_spread = max(source_laps) - min(source_laps)

        if lap_spread <= 3:
            confidence = 'High'
            achievable = True
            reason = f'Sectors from consecutive laps ({lap_spread} lap spread)'
        elif lap_spread <= 10:
            confidence = 'Medium'
            achievable = True
            reason = f'Moderate lap spread ({lap_spread} laps) - track evolution may affect'
        else:
            confidence = 'Low'
            achievable = True  # Still possible, but harder
            reason = f'Large lap spread ({lap_spread} laps) - setup/track changes likely'

        # Lap consistency metric
        lap_consistency = 100 - (lap_spread / len(self.best_sectors) * 10)

        return {
            'achievable': achievable,
            'confidence': confidence,
            'reason': reason,
            'lap_consistency': round(max(0, lap_consistency), 1),
            'unique_source_laps': len(unique_laps),
            'lap_spread': lap_spread
        }

    def create_delta_visualization(
        self,
        telemetry_df: pd.DataFrame,
        actual_lap_number: int,
        lap_column: str = 'LapNumber'
    ) -> go.Figure:
        """
        Delta map görselleştirme

        Args:
            telemetry_df: Full telemetry
            actual_lap_number: Lap to compare
            lap_column: Lap number column

        Returns:
            Plotly Figure
        """
        if self.perfect_lap_data is None:
            logger.error("Perfect lap not reconstructed")
            return go.Figure()

        actual_lap = telemetry_df[telemetry_df[lap_column] == actual_lap_number]

        if len(actual_lap) == 0:
            return go.Figure()

        # Align lengths
        min_len = min(len(actual_lap), len(self.perfect_lap_data))

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            subplot_titles=('Speed Comparison', 'Delta Map'),
            vertical_spacing=0.1,
            row_heights=[0.6, 0.4]
        )

        # Speed traces
        if 'Speed' in actual_lap.columns and 'Speed' in self.perfect_lap_data.columns:
            # Actual lap
            fig.add_trace(
                go.Scatter(
                    x=list(range(min_len)),
                    y=actual_lap['Speed'].iloc[:min_len],
                    mode='lines',
                    name=f'Actual Lap {actual_lap_number}',
                    line=dict(color='#FF6600', width=2)
                ),
                row=1,
                col=1
            )

            # Perfect lap
            fig.add_trace(
                go.Scatter(
                    x=list(range(min_len)),
                    y=self.perfect_lap_data['Speed'].iloc[:min_len],
                    mode='lines',
                    name='Perfect Lap (Theoretical)',
                    line=dict(color='#00FF00', width=2, dash='dash')
                ),
                row=1,
                col=1
            )

            # Delta calculation
            speed_delta = (
                self.perfect_lap_data['Speed'].iloc[:min_len].values -
                actual_lap['Speed'].iloc[:min_len].values
            )

            # Cumulative time delta (rough approximation)
            cumulative_delta = np.cumsum(speed_delta) / 1000  # Rough conversion

            # Delta map
            fig.add_trace(
                go.Scatter(
                    x=list(range(min_len)),
                    y=cumulative_delta,
                    mode='lines',
                    name='Time Delta (Cumulative)',
                    line=dict(color='#FF0000', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.2)'
                ),
                row=2,
                col=1
            )

            # Zero line
            fig.add_hline(
                y=0,
                line_dash='dot',
                line_color='white',
                row=2,
                col=1
            )

        fig.update_xaxes(title_text="Data Point", row=2, col=1)
        fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
        fig.update_yaxes(title_text="Delta (s)", row=2, col=1)

        fig.update_layout(
            title=f"Perfect Lap vs Actual Lap {actual_lap_number}",
            height=600,
            hovermode='x unified',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font={'color': '#FAFAFA'},
            showlegend=True
        )

        return fig

    def generate_improvement_plan(
        self,
        sector_deltas: List[Dict],
        top_n: int = 5
    ) -> str:
        """
        İyileştirme planı oluştur

        Args:
            sector_deltas: Sector delta list
            top_n: Number of priority sectors

        Returns:
            Formatted improvement plan
        """
        if not sector_deltas:
            return "No sector deltas available"

        plan = "=== IMPROVEMENT PLAN (Perfect Lap Target) ===\n\n"

        # Total potential
        total_gain = sum(d['delta'] for d in sector_deltas if d['delta'] > 0)
        plan += f"Total Time to Gain: {total_gain:.3f}s\n"
        plan += f"Target Theoretical Time: {self.theoretical_time:.3f}s\n\n"

        # Priority sectors
        plan += f"🎯 TOP {top_n} PRIORITY SECTORS:\n\n"

        worst_sectors = [d for d in sector_deltas if d['delta'] > 0][:top_n]

        for i, sector in enumerate(worst_sectors, 1):
            plan += f"{i}. Sector {sector['sector_id']}\n"
            plan += f"   Current: {sector['actual_time']:.3f}s\n"
            plan += f"   Target: {sector['perfect_time']:.3f}s\n"
            plan += f"   Gain: {sector['delta']:.3f}s\n"
            plan += f"   Best from: Lap {sector['perfect_from_lap']}\n"
            plan += f"   Status: {sector['status']}\n\n"

        # Achievability
        achievability = self.check_achievability()
        plan += f"\n📊 ACHIEVABILITY:\n"
        plan += f"Confidence: {achievability['confidence']}\n"
        plan += f"Reason: {achievability['reason']}\n"
        plan += f"Consistency: {achievability['lap_consistency']:.1f}%\n"

        return plan

    def export_perfect_lap_telemetry(
        self,
        output_path: str
    ) -> str:
        """
        Mükemmel tur telemetrisini export et

        Args:
            output_path: CSV output path

        Returns:
            Status message
        """
        if self.perfect_lap_data is None:
            return "❌ No perfect lap data to export"

        self.perfect_lap_data.to_csv(output_path, index=False)

        logger.info(f"Exported perfect lap telemetry: {output_path}")

        return f"✅ Exported {len(self.perfect_lap_data)} points to {output_path}"


# Test
if __name__ == "__main__":
    # Sample data
    sample_df = pd.DataFrame({
        'LapNumber': np.repeat(range(1, 6), 500),  # 5 laps
        'Sector': np.tile(np.repeat(range(1, 11), 50), 5),  # 10 sectors per lap
        'Speed': np.concatenate([
            np.random.normal(140 + lap, 15, 500)  # Speed improves with laps
            for lap in range(5)
        ])
    })

    reconstructor = PerfectLapReconstructor()

    # Identify best sectors
    print("=== IDENTIFYING BEST SECTORS ===")
    best_sectors = reconstructor.identify_best_sectors(sample_df)
    print(f"Found {len(best_sectors)} best sectors")

    for sector_id, info in list(best_sectors.items())[:3]:
        print(f"Sector {sector_id}: {info['sector_time']:.3f}s from Lap {info['best_lap']}")

    # Theoretical time
    print("\n=== THEORETICAL LAP TIME ===")
    theoretical = reconstructor.calculate_theoretical_lap_time()
    print(f"Theoretical best lap: {theoretical:.3f}s")

    # Reconstruct
    print("\n=== PERFECT LAP RECONSTRUCTION ===")
    perfect_lap = reconstructor.reconstruct_perfect_lap()
    print(f"Perfect lap data points: {len(perfect_lap)}")

    # Compare to actual lap
    print("\n=== COMPARISON TO LAP 3 ===")
    comparison = reconstructor.compare_to_actual_lap(sample_df, actual_lap_number=3)
    print(f"Actual time: {comparison['actual_time']:.3f}s")
    print(f"Perfect time: {comparison['perfect_time']:.3f}s")
    print(f"Delta: {comparison['time_delta']:.3f}s ({comparison['improvement_pct']:.1f}% slower)")

    # Sector deltas
    print("\n=== SECTOR DELTAS ===")
    sector_deltas = reconstructor.calculate_sector_deltas(sample_df, actual_lap_number=3)
    for delta in sector_deltas[:5]:
        print(f"Sector {delta['sector_id']}: {delta['delta']:+.3f}s - {delta['status']}")

    # Achievability
    print("\n=== ACHIEVABILITY ===")
    achievability = reconstructor.check_achievability()
    print(f"Confidence: {achievability['confidence']}")
    print(f"Reason: {achievability['reason']}")

    # Improvement plan
    print("\n" + reconstructor.generate_improvement_plan(sector_deltas, top_n=3))
