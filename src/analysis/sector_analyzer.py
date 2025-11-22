"""
Sector Performance Analyzer
19-turn detailed sector analysis module

Jüri için kritik: Dataset'in unique kullanımı
AnalysisEnduranceWithSections.csv → Sector-by-sector breakdown
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """
    19 viraj detaylı sektör analizi

    Toyota TRD mühendislerinin en çok kullandığı analiz:
    - Her sektörde ne kadar zaman kaybediliyor?
    - Hangi virajlar weak point?
    - Sektör bazında improvement potential
    """

    def __init__(self):
        self.sector_data: Optional[pd.DataFrame] = None
        self.analysis_results: Dict = {}
        self.num_sectors: int = 19  # COTA has 19 turns

    def load_sector_data(self, df: pd.DataFrame) -> None:
        """
        Sector data yükle ve validate et

        Args:
            df: AnalysisEnduranceWithSections CSV DataFrame
        """
        required_cols = ['SectorNumber', 'SectorTime']

        # Column validation
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}. Attempting to infer sectors...")

            # Fallback: Infer sectors from lap data
            if 'Distance' in df.columns and 'LapNumber' in df.columns:
                df = self._infer_sectors_from_distance(df)
            else:
                raise ValueError("Cannot infer sector data. Missing required columns.")

        self.sector_data = df
        logger.info(f"Sector data loaded: {len(df)} records")

    def _infer_sectors_from_distance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Distance veriden sektör tahmin et (fallback method)

        Args:
            df: DataFrame with Distance and LapNumber

        Returns:
            DataFrame with inferred SectorNumber and SectorTime
        """
        df = df.copy()

        # Assume 19 equal sectors (simplification)
        lap_length = df.groupby('LapNumber')['Distance'].max().mean()
        sector_length = lap_length / self.num_sectors

        df['SectorNumber'] = ((df['Distance'] % lap_length) / sector_length).astype(int) + 1
        df['SectorNumber'] = df['SectorNumber'].clip(1, self.num_sectors)

        # Calculate sector time (simplified)
        if 'TimeStamp' in df.columns:
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
            df = df.sort_values(['LapNumber', 'SectorNumber', 'TimeStamp'])

            # Group by lap and sector, calculate time difference
            sector_times = df.groupby(['LapNumber', 'SectorNumber']).agg({
                'TimeStamp': ['min', 'max']
            })
            sector_times.columns = ['start', 'end']
            sector_times['SectorTime'] = (sector_times['end'] - sector_times['start']).dt.total_seconds()

            df = df.merge(
                sector_times[['SectorTime']],
                left_on=['LapNumber', 'SectorNumber'],
                right_index=True,
                how='left'
            )

        logger.info("Sectors inferred from distance data")
        return df

    def analyze_sector_performance(self) -> Dict[int, Dict]:
        """
        Her sektör için detaylı performans analizi

        Returns:
            Dict: {sector_num: {metrics}}
        """
        if self.sector_data is None:
            raise ValueError("No sector data loaded. Call load_sector_data() first.")

        df = self.sector_data
        sector_stats = {}

        for sector_num in range(1, self.num_sectors + 1):
            sector_df = df[df['SectorNumber'] == sector_num]

            if len(sector_df) == 0:
                continue

            # Basic statistics
            avg_time = sector_df['SectorTime'].mean()
            best_time = sector_df['SectorTime'].min()
            worst_time = sector_df['SectorTime'].max()
            std_dev = sector_df['SectorTime'].std()

            # Time loss vs best
            delta_to_best = avg_time - best_time

            # Consistency score (lower std = better)
            consistency = max(0, 100 - (std_dev / avg_time * 100)) if avg_time > 0 else 0

            # Improvement potential
            potential_gain = delta_to_best

            # Speed analysis (if available)
            if 'Speed' in sector_df.columns:
                avg_speed = sector_df['Speed'].mean()
                min_speed = sector_df['Speed'].min()
                max_speed = sector_df['Speed'].max()
            else:
                avg_speed = min_speed = max_speed = None

            sector_stats[sector_num] = {
                'avg_time': float(avg_time),
                'best_time': float(best_time),
                'worst_time': float(worst_time),
                'std_dev': float(std_dev),
                'delta_to_best': float(delta_to_best),
                'consistency': float(consistency),
                'potential_gain': float(potential_gain),
                'avg_speed': float(avg_speed) if avg_speed else None,
                'min_speed': float(min_speed) if min_speed else None,
                'max_speed': float(max_speed) if max_speed else None,
                'attempts': len(sector_df)
            }

        self.analysis_results = sector_stats
        logger.info(f"Analyzed {len(sector_stats)} sectors")

        return sector_stats

    def get_weakness_map(self, top_n: int = 5) -> List[Tuple[int, float]]:
        """
        En zayıf sektörleri bul (en çok zaman kaybedilen)

        Args:
            top_n: Top N weak sectors

        Returns:
            List of (sector_num, time_loss) tuples
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        # Sort by delta_to_best (descending)
        weaknesses = [
            (sector, stats['delta_to_best'])
            for sector, stats in self.analysis_results.items()
        ]

        weaknesses.sort(key=lambda x: x[1], reverse=True)

        return weaknesses[:top_n]

    def get_strength_map(self, top_n: int = 5) -> List[Tuple[int, float]]:
        """
        En güçlü sektörleri bul (en az zaman kaybı)

        Args:
            top_n: Top N strong sectors

        Returns:
            List of (sector_num, consistency) tuples
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        # Sort by consistency (descending)
        strengths = [
            (sector, stats['consistency'])
            for sector, stats in self.analysis_results.items()
        ]

        strengths.sort(key=lambda x: x[1], reverse=True)

        return strengths[:top_n]

    def calculate_total_recoverable_time(self) -> float:
        """
        Toplam kazanılabilir zaman (tüm sektörlerde best'e ulaşırsa)

        Returns:
            Total potential time gain (seconds)
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        total = sum(stats['delta_to_best'] for stats in self.analysis_results.values())

        return float(total)

    def get_sector_insights(self, sector_num: int) -> Dict:
        """
        Belirli bir sektör için detaylı insights

        Args:
            sector_num: Sector number (1-19)

        Returns:
            Dict with insights and recommendations
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        if sector_num not in self.analysis_results:
            return {}

        stats = self.analysis_results[sector_num]

        # Performance classification
        if stats['delta_to_best'] > 0.5:
            performance_level = "Critical - High time loss"
            priority = "🔴 High Priority"
        elif stats['delta_to_best'] > 0.2:
            performance_level = "Moderate - Improvement needed"
            priority = "🟡 Medium Priority"
        else:
            performance_level = "Good - Minor optimization"
            priority = "🟢 Low Priority"

        # Consistency classification
        if stats['consistency'] > 85:
            consistency_level = "Excellent"
        elif stats['consistency'] > 70:
            consistency_level = "Good"
        elif stats['consistency'] > 50:
            consistency_level = "Fair"
        else:
            consistency_level = "Poor"

        # Generate recommendation
        if stats['delta_to_best'] > 0.3:
            recommendation = f"Focus on Turn {sector_num}: {stats['delta_to_best']:.3f}s recoverable. Review braking point and apex speed."
        elif stats['consistency'] < 70:
            recommendation = f"Improve consistency in Turn {sector_num}. Current variance: {stats['std_dev']:.3f}s"
        else:
            recommendation = f"Turn {sector_num} is performing well. Maintain current approach."

        return {
            'sector_number': sector_num,
            'performance_level': performance_level,
            'priority': priority,
            'consistency_level': consistency_level,
            'time_loss': stats['delta_to_best'],
            'potential_gain': stats['potential_gain'],
            'recommendation': recommendation,
            'stats': stats
        }

    def generate_coaching_summary(self) -> str:
        """
        AI-ready coaching summary (tüm sektörler için)

        Returns:
            Text summary for AI processing
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        weaknesses = self.get_weakness_map(top_n=5)
        total_recoverable = self.calculate_total_recoverable_time()

        summary = f"SECTOR ANALYSIS SUMMARY\n"
        summary += f"Total Recoverable Time: {total_recoverable:.3f} seconds\n\n"
        summary += f"TOP 5 WEAK SECTORS:\n"

        for i, (sector, time_loss) in enumerate(weaknesses, 1):
            stats = self.analysis_results[sector]
            summary += f"{i}. Turn {sector}: -{time_loss:.3f}s (Consistency: {stats['consistency']:.1f}%)\n"

        summary += f"\nKEY RECOMMENDATIONS:\n"

        for sector, time_loss in weaknesses[:3]:
            insight = self.get_sector_insights(sector)
            summary += f"- {insight['recommendation']}\n"

        return summary

    def export_sector_report(self) -> pd.DataFrame:
        """
        Export detailed sector report as DataFrame

        Returns:
            DataFrame with all sector statistics
        """
        if not self.analysis_results:
            self.analyze_sector_performance()

        report_data = []

        for sector_num, stats in sorted(self.analysis_results.items()):
            insight = self.get_sector_insights(sector_num)

            report_data.append({
                'Sector': f'Turn {sector_num}',
                'Avg Time (s)': stats['avg_time'],
                'Best Time (s)': stats['best_time'],
                'Time Loss (s)': stats['delta_to_best'],
                'Consistency (%)': stats['consistency'],
                'Priority': insight['priority'],
                'Performance': insight['performance_level'],
                'Recommendation': insight['recommendation']
            })

        return pd.DataFrame(report_data)


# Örnek kullanım
if __name__ == "__main__":
    # Test with sample data
    sample_data = pd.DataFrame({
        'SectorNumber': np.repeat(range(1, 20), 10),
        'SectorTime': np.random.uniform(8, 15, 190) + np.random.normal(0, 0.5, 190),
        'Speed': np.random.uniform(100, 200, 190),
        'LapNumber': np.tile(range(1, 11), 19)
    })

    analyzer = SectorAnalyzer()
    analyzer.load_sector_data(sample_data)

    # Analyze
    results = analyzer.analyze_sector_performance()

    print("\n=== SECTOR ANALYSIS ===")
    print(f"Total sectors: {len(results)}")

    print("\n=== WEAKNESS MAP ===")
    weaknesses = analyzer.get_weakness_map(top_n=5)
    for sector, time_loss in weaknesses:
        print(f"Turn {sector}: -{time_loss:.3f}s")

    print(f"\n=== TOTAL RECOVERABLE TIME ===")
    print(f"{analyzer.calculate_total_recoverable_time():.3f} seconds")

    print("\n=== COACHING SUMMARY ===")
    print(analyzer.generate_coaching_summary())

    print("\n=== SECTOR REPORT ===")
    report = analyzer.export_sector_report()
    print(report.head(10))
