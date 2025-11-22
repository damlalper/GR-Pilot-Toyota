"""
Lap Comparison Tool
Side-by-side telemetry and delta analysis

GERÇEK KULLANIM:
Best lap vs current lap
Driver A vs Driver B
Setup A vs Setup B
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class LapComparator:
    """
    2 tur karşılaştırma aracı

    Toyota engineers kullanır:
    - Best vs current lap
    - Setup change validation
    - Driver comparison
    """

    def __init__(self):
        self.lap_a_data: Optional[pd.DataFrame] = None
        self.lap_b_data: Optional[pd.DataFrame] = None
        self.delta_data: Optional[pd.DataFrame] = None

    def load_laps(
        self,
        df: pd.DataFrame,
        lap_a_num: int,
        lap_b_num: int
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        2 turu yükle

        Args:
            df: Full telemetry DataFrame
            lap_a_num: First lap number
            lap_b_num: Second lap number

        Returns:
            Tuple of (lap_a_df, lap_b_df)
        """
        if 'LapNumber' not in df.columns:
            raise ValueError("LapNumber column required")

        self.lap_a_data = df[df['LapNumber'] == lap_a_num].copy()
        self.lap_b_data = df[df['LapNumber'] == lap_b_num].copy()

        if len(self.lap_a_data) == 0 or len(self.lap_b_data) == 0:
            raise ValueError("One or both laps not found in data")

        return self.lap_a_data, self.lap_b_data

    def calculate_delta_time(
        self,
        metric: str = 'Speed'
    ) -> pd.DataFrame:
        """
        Delta time hesaplama (cumulative)

        Args:
            metric: Metric to compare (Speed, BrakePressure, etc.)

        Returns:
            DataFrame with delta calculations
        """
        if self.lap_a_data is None or self.lap_b_data is None:
            raise ValueError("Load laps first with load_laps()")

        if metric not in self.lap_a_data.columns or metric not in self.lap_b_data.columns:
            raise ValueError(f"{metric} not found in lap data")

        # Align lengths (use shorter)
        min_len = min(len(self.lap_a_data), len(self.lap_b_data))

        lap_a_values = self.lap_a_data[metric].iloc[:min_len].values
        lap_b_values = self.lap_b_data[metric].iloc[:min_len].values

        # Instant delta
        instant_delta = lap_a_values - lap_b_values

        # Cumulative delta (if speed)
        if metric == 'Speed':
            # Approximate time delta from speed difference
            # Assumes constant sampling rate
            cumulative_delta = np.cumsum(instant_delta) / 100  # Rough conversion
        else:
            cumulative_delta = instant_delta

        self.delta_data = pd.DataFrame({
            'point': range(min_len),
            'lap_a': lap_a_values,
            'lap_b': lap_b_values,
            'instant_delta': instant_delta,
            'cumulative_delta': cumulative_delta
        })

        return self.delta_data

    def find_key_differences(
        self,
        threshold: float = 10.0
    ) -> Dict[str, list]:
        """
        Ana farkları bul

        Args:
            threshold: Minimum delta threshold

        Returns:
            Dict with key differences
        """
        if self.delta_data is None:
            raise ValueError("Calculate delta first")

        differences = {
            'lap_a_faster': [],
            'lap_b_faster': [],
            'biggest_gains': [],
            'biggest_losses': []
        }

        # Find regions where each lap is faster
        lap_a_faster_mask = self.delta_data['instant_delta'] > threshold
        lap_b_faster_mask = self.delta_data['instant_delta'] < -threshold

        differences['lap_a_faster'] = self.delta_data[lap_a_faster_mask]['point'].tolist()
        differences['lap_b_faster'] = self.delta_data[lap_b_faster_mask]['point'].tolist()

        # Biggest gains/losses
        max_gain_idx = self.delta_data['cumulative_delta'].idxmax()
        max_loss_idx = self.delta_data['cumulative_delta'].idxmin()

        differences['biggest_gains'].append({
            'point': int(max_gain_idx),
            'delta': float(self.delta_data.loc[max_gain_idx, 'cumulative_delta'])
        })

        differences['biggest_losses'].append({
            'point': int(max_loss_idx),
            'delta': float(self.delta_data.loc[max_loss_idx, 'cumulative_delta'])
        })

        return differences

    def create_comparison_chart(
        self,
        channels: list = ['Speed', 'BrakePressure', 'Throttle']
    ) -> go.Figure:
        """
        Comparison visualization

        Args:
            channels: Channels to compare

        Returns:
            Plotly Figure
        """
        if self.lap_a_data is None or self.lap_b_data is None:
            raise ValueError("Load laps first")

        # Filter available channels
        available = [ch for ch in channels if ch in self.lap_a_data.columns and ch in self.lap_b_data.columns]

        if not available:
            raise ValueError("No valid channels to plot")

        fig = make_subplots(
            rows=len(available),
            cols=1,
            shared_xaxes=True,
            subplot_titles=available,
            vertical_spacing=0.05
        )

        colors_a = ['#FF0000', '#FF6600', '#FFAA00']
        colors_b = ['#0066CC', '#0099CC', '#00CCCC']

        min_len = min(len(self.lap_a_data), len(self.lap_b_data))

        for i, channel in enumerate(available):
            # Lap A
            fig.add_trace(
                go.Scatter(
                    x=list(range(min_len)),
                    y=self.lap_a_data[channel].iloc[:min_len],
                    mode='lines',
                    name=f'Lap A - {channel}',
                    line=dict(color=colors_a[i % 3], width=2),
                    showlegend=(i == 0)
                ),
                row=i+1,
                col=1
            )

            # Lap B
            fig.add_trace(
                go.Scatter(
                    x=list(range(min_len)),
                    y=self.lap_b_data[channel].iloc[:min_len],
                    mode='lines',
                    name=f'Lap B - {channel}',
                    line=dict(color=colors_b[i % 3], width=2, dash='dash'),
                    showlegend=(i == 0)
                ),
                row=i+1,
                col=1
            )

            fig.update_yaxes(title_text=channel, row=i+1, col=1)

        fig.update_xaxes(title_text="Data Point", row=len(available), col=1)

        fig.update_layout(
            title="Lap Comparison - Side by Side",
            height=200 * len(available),
            hovermode='x unified',
            plot_bgcolor='#262730',
            paper_bgcolor='#0E1117',
            font={'color': '#FAFAFA'}
        )

        return fig

    def generate_comparison_report(self) -> str:
        """
        Text comparison report

        Returns:
            Formatted text report
        """
        if self.lap_a_data is None or self.lap_b_data is None:
            return "No laps loaded"

        report = "=== LAP COMPARISON REPORT ===\n\n"

        # Speed comparison
        if 'Speed' in self.lap_a_data.columns:
            avg_speed_a = self.lap_a_data['Speed'].mean()
            avg_speed_b = self.lap_b_data['Speed'].mean()
            speed_delta = avg_speed_a - avg_speed_b

            report += f"SPEED:\n"
            report += f"Lap A avg: {avg_speed_a:.1f} km/h\n"
            report += f"Lap B avg: {avg_speed_b:.1f} km/h\n"
            report += f"Delta: {speed_delta:+.1f} km/h\n\n"

        # Brake comparison
        if 'BrakePressure' in self.lap_a_data.columns:
            avg_brake_a = self.lap_a_data[self.lap_a_data['BrakePressure'] > 0]['BrakePressure'].mean()
            avg_brake_b = self.lap_b_data[self.lap_b_data['BrakePressure'] > 0]['BrakePressure'].mean()

            report += f"BRAKING:\n"
            report += f"Lap A avg: {avg_brake_a:.1f} bar\n"
            report += f"Lap B avg: {avg_brake_b:.1f} bar\n"
            report += f"Delta: {avg_brake_a - avg_brake_b:+.1f} bar\n\n"

        # Key differences
        if self.delta_data is not None:
            diffs = self.find_key_differences()

            report += f"KEY DIFFERENCES:\n"
            if diffs['biggest_gains']:
                report += f"Biggest gain: {diffs['biggest_gains'][0]['delta']:.3f}s at point {diffs['biggest_gains'][0]['point']}\n"
            if diffs['biggest_losses']:
                report += f"Biggest loss: {diffs['biggest_losses'][0]['delta']:.3f}s at point {diffs['biggest_losses'][0]['point']}\n"

        # Winner
        if 'Speed' in self.lap_a_data.columns:
            if avg_speed_a > avg_speed_b:
                report += f"\n✅ LAP A IS FASTER (+{abs(speed_delta):.1f} km/h avg)\n"
            else:
                report += f"\n✅ LAP B IS FASTER (+{abs(speed_delta):.1f} km/h avg)\n"

        return report


# Test
if __name__ == "__main__":
    # Sample data
    sample_df = pd.DataFrame({
        'LapNumber': np.repeat([1, 2], 500),
        'Speed': np.concatenate([
            np.random.normal(150, 10, 500),
            np.random.normal(155, 8, 500)
        ]),
        'BrakePressure': np.random.uniform(0, 100, 1000),
        'Throttle': np.random.uniform(0, 100, 1000)
    })

    comparator = LapComparator()

    # Load laps
    lap_a, lap_b = comparator.load_laps(sample_df, lap_a_num=1, lap_b_num=2)
    print(f"Loaded: Lap A ({len(lap_a)} points), Lap B ({len(lap_b)} points)")

    # Calculate delta
    delta_df = comparator.calculate_delta_time('Speed')
    print(f"\nDelta calculated: {len(delta_df)} points")

    # Report
    print("\n" + comparator.generate_comparison_report())
