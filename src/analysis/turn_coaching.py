"""
Turn-by-Turn Coaching System
Structured coaching for all 19 turns at COTA

GERÇEK TOYOTA TRD MÜHENDİSLİK:
Her viraj için:
- Brake point analysis
- Throttle application timing
- Steering input quality
- Speed optimization
- Track position recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TurnCoachingSystem:
    """
    19 viraj için detaylı coaching sistemi

    Toyota TRD engineers kullanır:
    - Her viraj için spesifik tavsiyeler
    - Brake/throttle/steering analizi
    - Track position optimization
    - Data-driven coaching
    """

    def __init__(self):
        # COTA 19-turn configuration
        self.turn_database = self._initialize_turn_database()
        self.coaching_history: List[Dict] = []

    def _initialize_turn_database(self) -> Dict[int, Dict]:
        """
        Circuit of The Americas - 19 viraj database

        Her viraj için:
        - Type (hairpin, fast sweeper, technical)
        - Optimal speed range
        - Brake point guidance
        - Key characteristics

        Returns:
            Dict with turn configurations
        """
        return {
            1: {
                'name': 'Turn 1',
                'type': 'slow_left',
                'optimal_speed_range': (60, 80),  # km/h
                'brake_point_distance': 120,  # meters before apex
                'difficulty': 'medium',
                'key_tip': 'Late apex, wide entry for T2 setup',
                'common_mistake': 'Braking too early, missing apex speed'
            },
            2: {
                'name': 'Turn 2',
                'type': 'fast_right',
                'optimal_speed_range': (120, 145),
                'brake_point_distance': 0,  # Lift only
                'difficulty': 'easy',
                'key_tip': 'Committed lift, trust the grip',
                'common_mistake': 'Over-slowing, losing momentum to T3'
            },
            3: {
                'name': 'Turn 3-5 (Esses)',
                'type': 'technical_complex',
                'optimal_speed_range': (100, 130),
                'brake_point_distance': 50,
                'difficulty': 'hard',
                'key_tip': 'Flow and rhythm critical, minimize steering corrections',
                'common_mistake': 'Too aggressive T3 entry, compromising T5 exit'
            },
            6: {
                'name': 'Turn 6',
                'type': 'fast_left',
                'optimal_speed_range': (160, 185),
                'brake_point_distance': 0,
                'difficulty': 'medium',
                'key_tip': 'Full commitment, slight lift if needed',
                'common_mistake': 'Lifting too much, scrubbing speed'
            },
            7: {
                'name': 'Turn 7',
                'type': 'fast_right',
                'optimal_speed_range': (155, 175),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Smooth arc, maintain throttle',
                'common_mistake': 'Early turn-in, running wide'
            },
            8: {
                'name': 'Turn 8',
                'type': 'fast_left',
                'optimal_speed_range': (150, 170),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Constant radius, smooth inputs',
                'common_mistake': 'Jerky steering, upsetting balance'
            },
            9: {
                'name': 'Turn 9',
                'type': 'fast_right',
                'optimal_speed_range': (145, 165),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Flow from T8, maintain momentum',
                'common_mistake': 'Over-correcting from T8'
            },
            10: {
                'name': 'Turn 10',
                'type': 'slow_left',
                'optimal_speed_range': (65, 85),
                'brake_point_distance': 100,
                'difficulty': 'medium',
                'key_tip': 'Trail braking opportunity, late apex',
                'common_mistake': 'Braking too hard, locking fronts'
            },
            11: {
                'name': 'Turn 11 (Hairpin)',
                'type': 'hairpin_left',
                'optimal_speed_range': (55, 70),
                'brake_point_distance': 150,
                'difficulty': 'hard',
                'key_tip': 'CRITICAL: Exit speed determines back straight time',
                'common_mistake': 'Too much entry speed, compromising exit'
            },
            12: {
                'name': 'Turn 12',
                'type': 'fast_left',
                'optimal_speed_range': (140, 160),
                'brake_point_distance': 0,
                'difficulty': 'medium',
                'key_tip': 'Downhill compression, trust grip',
                'common_mistake': 'Lifting mid-corner, losing time'
            },
            13: {
                'name': 'Turn 13',
                'type': 'medium_right',
                'optimal_speed_range': (110, 130),
                'brake_point_distance': 60,
                'difficulty': 'medium',
                'key_tip': 'Setup for T14-15 complex',
                'common_mistake': 'Not enough rotation, wide T14 entry'
            },
            14: {
                'name': 'Turn 14',
                'type': 'slow_left',
                'optimal_speed_range': (75, 95),
                'brake_point_distance': 80,
                'difficulty': 'medium',
                'key_tip': 'Downhill braking, ABS management',
                'common_mistake': 'Brake lock, flat-spotting tires'
            },
            15: {
                'name': 'Turn 15 (Hairpin)',
                'type': 'hairpin_right',
                'optimal_speed_range': (60, 75),
                'brake_point_distance': 120,
                'difficulty': 'hard',
                'key_tip': 'Long acceleration zone ahead, maximize exit',
                'common_mistake': 'Early turn-in, apexing too soon'
            },
            16: {
                'name': 'Turn 16',
                'type': 'fast_left',
                'optimal_speed_range': (135, 155),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Flat out in most conditions',
                'common_mistake': 'Unnecessary lift, losing momentum'
            },
            17: {
                'name': 'Turn 17',
                'type': 'fast_right',
                'optimal_speed_range': (140, 160),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Smooth transition from T16',
                'common_mistake': 'Abrupt steering change'
            },
            18: {
                'name': 'Turn 18',
                'type': 'fast_left',
                'optimal_speed_range': (145, 165),
                'brake_point_distance': 0,
                'difficulty': 'easy',
                'key_tip': 'Final fast section, build confidence',
                'common_mistake': 'Lifting due to lack of confidence'
            },
            19: {
                'name': 'Turn 19',
                'type': 'medium_right',
                'optimal_speed_range': (100, 120),
                'brake_point_distance': 70,
                'difficulty': 'medium',
                'key_tip': 'Exit onto main straight - CRITICAL for lap time',
                'common_mistake': 'Too much speed mid-corner, poor exit'
            }
        }

    def analyze_turn_performance(
        self,
        turn_number: int,
        turn_data: pd.DataFrame
    ) -> Dict:
        """
        Tek viraj için detaylı performans analizi

        Args:
            turn_number: Turn ID (1-19)
            turn_data: DataFrame for this turn (Speed, BrakePressure, Throttle, SteeringAngle)

        Returns:
            Dict with performance metrics + coaching
        """
        if turn_number not in self.turn_database:
            logger.warning(f"Turn {turn_number} not in database")
            return {}

        turn_config = self.turn_database[turn_number]

        # Extract metrics
        metrics = self._extract_turn_metrics(turn_data, turn_config)

        # Generate coaching
        coaching = self._generate_turn_coaching(
            turn_number,
            metrics,
            turn_config
        )

        return {
            'turn_number': turn_number,
            'turn_name': turn_config['name'],
            'metrics': metrics,
            'coaching': coaching,
            'grade': self._calculate_turn_grade(metrics, turn_config)
        }

    def _extract_turn_metrics(
        self,
        turn_data: pd.DataFrame,
        turn_config: Dict
    ) -> Dict:
        """
        Virajdan metrik çıkarma

        Args:
            turn_data: Turn telemetry
            turn_config: Turn configuration

        Returns:
            Dict with extracted metrics
        """
        metrics = {}

        # Speed analysis
        if 'Speed' in turn_data.columns:
            metrics['min_speed'] = float(turn_data['Speed'].min())
            metrics['max_speed'] = float(turn_data['Speed'].max())
            metrics['avg_speed'] = float(turn_data['Speed'].mean())

            # Optimal range check
            optimal_min, optimal_max = turn_config['optimal_speed_range']
            if metrics['min_speed'] < optimal_min:
                metrics['speed_status'] = 'too_slow'
                metrics['speed_delta'] = optimal_min - metrics['min_speed']
            elif metrics['min_speed'] > optimal_max:
                metrics['speed_status'] = 'too_fast'
                metrics['speed_delta'] = metrics['min_speed'] - optimal_max
            else:
                metrics['speed_status'] = 'optimal'
                metrics['speed_delta'] = 0

        # Brake analysis
        if 'BrakePressure' in turn_data.columns:
            brake_events = turn_data[turn_data['BrakePressure'] > 10]

            if len(brake_events) > 0:
                metrics['max_brake_pressure'] = float(brake_events['BrakePressure'].max())
                metrics['avg_brake_pressure'] = float(brake_events['BrakePressure'].mean())
                metrics['brake_application_length'] = len(brake_events)

                # Brake smoothness (variance)
                if len(brake_events) > 1:
                    brake_changes = brake_events['BrakePressure'].diff().abs()
                    metrics['brake_smoothness'] = 100 - float(brake_changes.mean())
                else:
                    metrics['brake_smoothness'] = 100
            else:
                metrics['max_brake_pressure'] = 0
                metrics['brake_application_length'] = 0
                metrics['brake_smoothness'] = 100  # No braking = smooth

        # Throttle analysis
        if 'Throttle' in turn_data.columns:
            # Find throttle application point (when throttle > 50% after minimum)
            min_speed_idx = turn_data['Speed'].idxmin() if 'Speed' in turn_data.columns else 0

            post_apex = turn_data.loc[min_speed_idx:]
            if len(post_apex) > 0 and 'Throttle' in post_apex.columns:
                throttle_on = post_apex[post_apex['Throttle'] > 50]
                if len(throttle_on) > 0:
                    metrics['throttle_application_point'] = 'early' if len(throttle_on) > len(post_apex) * 0.7 else 'late'
                else:
                    metrics['throttle_application_point'] = 'none'

            # Throttle smoothness
            if len(turn_data) > 1:
                throttle_changes = turn_data['Throttle'].diff().abs()
                metrics['throttle_smoothness'] = 100 - float(throttle_changes.mean())
            else:
                metrics['throttle_smoothness'] = 100

        # Steering analysis
        if 'SteeringAngle' in turn_data.columns:
            metrics['max_steering_angle'] = float(turn_data['SteeringAngle'].abs().max())

            # Steering corrections (rapid changes)
            if len(turn_data) > 1:
                steering_changes = turn_data['SteeringAngle'].diff().abs()
                corrections = steering_changes[steering_changes > 5]  # >5° changes
                metrics['steering_corrections'] = len(corrections)
                metrics['steering_smoothness'] = 100 - (len(corrections) / len(turn_data) * 100)
            else:
                metrics['steering_corrections'] = 0
                metrics['steering_smoothness'] = 100

        return metrics

    def _generate_turn_coaching(
        self,
        turn_number: int,
        metrics: Dict,
        turn_config: Dict
    ) -> Dict:
        """
        Metriklerden coaching üret

        Args:
            turn_number: Turn number
            metrics: Extracted metrics
            turn_config: Turn configuration

        Returns:
            Dict with coaching recommendations
        """
        coaching = {
            'primary_issue': None,
            'recommendations': [],
            'strong_points': [],
            'priority': 'medium'
        }

        # Speed coaching
        if 'speed_status' in metrics:
            if metrics['speed_status'] == 'too_slow':
                coaching['primary_issue'] = f"Minimum speed {metrics['speed_delta']:.1f} km/h below optimal"
                coaching['recommendations'].append(
                    f"🏎️ Brake {turn_config['brake_point_distance'] - 10}m later to carry more speed"
                )
                coaching['recommendations'].append(
                    "⚡ Trust the grip - you can carry more speed through apex"
                )
                coaching['priority'] = 'high'

            elif metrics['speed_status'] == 'too_fast':
                coaching['primary_issue'] = f"Entry speed {metrics['speed_delta']:.1f} km/h too high"
                coaching['recommendations'].append(
                    f"🛑 Brake {turn_config['brake_point_distance'] + 10}m earlier"
                )
                coaching['recommendations'].append(
                    "🎯 Focus on exit speed, not entry speed"
                )
                coaching['priority'] = 'high'

            else:
                coaching['strong_points'].append(
                    f"✅ Excellent minimum speed ({metrics['min_speed']:.1f} km/h)"
                )

        # Brake coaching
        if 'brake_smoothness' in metrics:
            if metrics['brake_smoothness'] < 70:
                coaching['recommendations'].append(
                    "🔧 Brake application too abrupt - smoother initial pressure"
                )
            else:
                coaching['strong_points'].append(
                    f"✅ Good brake control (smoothness: {metrics['brake_smoothness']:.0f}%)"
                )

        # Throttle coaching
        if 'throttle_smoothness' in metrics:
            if metrics['throttle_smoothness'] < 75:
                coaching['recommendations'].append(
                    "⚙️ Throttle too aggressive - progressive application needed"
                )

        # Steering coaching
        if 'steering_corrections' in metrics:
            if metrics['steering_corrections'] > 3:
                coaching['recommendations'].append(
                    f"🎮 {metrics['steering_corrections']} steering corrections - aim for single smooth arc"
                )
                coaching['priority'] = 'high'
            else:
                coaching['strong_points'].append(
                    "✅ Clean steering input - minimal corrections"
                )

        # Turn-specific tip
        coaching['recommendations'].append(
            f"💡 {turn_config['key_tip']}"
        )

        # Common mistake warning
        if not coaching['strong_points']:  # If struggling
            coaching['recommendations'].append(
                f"⚠️ Avoid: {turn_config['common_mistake']}"
            )

        return coaching

    def _calculate_turn_grade(
        self,
        metrics: Dict,
        turn_config: Dict
    ) -> str:
        """
        Viraj notu hesapla (A-F)

        Args:
            metrics: Performance metrics
            turn_config: Turn configuration

        Returns:
            Grade string
        """
        score = 0
        max_score = 0

        # Speed score (40 points)
        if 'speed_status' in metrics:
            max_score += 40
            if metrics['speed_status'] == 'optimal':
                score += 40
            elif metrics['speed_delta'] < 5:
                score += 30
            elif metrics['speed_delta'] < 10:
                score += 20
            else:
                score += 10

        # Brake smoothness (20 points)
        if 'brake_smoothness' in metrics:
            max_score += 20
            score += (metrics['brake_smoothness'] / 100) * 20

        # Throttle smoothness (20 points)
        if 'throttle_smoothness' in metrics:
            max_score += 20
            score += (metrics['throttle_smoothness'] / 100) * 20

        # Steering smoothness (20 points)
        if 'steering_smoothness' in metrics:
            max_score += 20
            score += (metrics['steering_smoothness'] / 100) * 20

        if max_score == 0:
            return 'N/A'

        percentage = (score / max_score) * 100

        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def analyze_all_turns(
        self,
        telemetry_df: pd.DataFrame,
        sector_column: str = 'Sector'
    ) -> List[Dict]:
        """
        Tüm virajları analiz et

        Args:
            telemetry_df: Full telemetry DataFrame
            sector_column: Column name with sector/turn IDs

        Returns:
            List of turn analysis dicts
        """
        all_turns = []

        if sector_column not in telemetry_df.columns:
            logger.warning(f"{sector_column} column not found - cannot analyze turns")
            return []

        for turn_num in range(1, 20):  # 19 turns
            turn_data = telemetry_df[telemetry_df[sector_column] == turn_num]

            if len(turn_data) > 0:
                analysis = self.analyze_turn_performance(turn_num, turn_data)
                all_turns.append(analysis)
            else:
                logger.debug(f"No data for turn {turn_num}")

        self.coaching_history = all_turns
        logger.info(f"Analyzed {len(all_turns)} turns")

        return all_turns

    def get_priority_coaching(
        self,
        top_n: int = 5
    ) -> List[Dict]:
        """
        En önemli coaching noktaları

        Args:
            top_n: Number of priority turns

        Returns:
            List of priority turn coaching
        """
        if not self.coaching_history:
            return []

        # Sort by priority (high > medium > low) and grade (F > A)
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        grade_map = {'F': 5, 'D': 4, 'C': 3, 'B': 2, 'A': 1, 'N/A': 0}

        sorted_turns = sorted(
            self.coaching_history,
            key=lambda x: (
                priority_map.get(x['coaching']['priority'], 0),
                grade_map.get(x['grade'], 0)
            ),
            reverse=True
        )

        return sorted_turns[:top_n]

    def generate_full_coaching_report(self) -> str:
        """
        Tam coaching raporu

        Returns:
            Formatted text report
        """
        if not self.coaching_history:
            return "No turn data analyzed yet"

        report = "=== TURN-BY-TURN COACHING REPORT ===\n\n"

        # Overall summary
        grades = [t['grade'] for t in self.coaching_history if t['grade'] != 'N/A']
        avg_grade = sum(ord(g) for g in grades) / len(grades) if grades else 0

        report += f"Turns Analyzed: {len(self.coaching_history)}/19\n"
        report += f"Average Performance: {chr(int(avg_grade)) if avg_grade > 0 else 'N/A'}\n\n"

        # Priority coaching
        report += "🔥 PRIORITY IMPROVEMENTS:\n"
        priority_turns = self.get_priority_coaching(top_n=5)

        for i, turn in enumerate(priority_turns, 1):
            report += f"\n{i}. {turn['turn_name']} (Grade: {turn['grade']})\n"

            if turn['coaching']['primary_issue']:
                report += f"   Issue: {turn['coaching']['primary_issue']}\n"

            for rec in turn['coaching']['recommendations'][:2]:  # Top 2 recommendations
                report += f"   → {rec}\n"

        # Strong points
        report += "\n\n✅ STRONG POINTS:\n"
        strong_turns = [t for t in self.coaching_history if t['grade'] in ['A', 'B']]

        for turn in strong_turns[:3]:
            report += f"• {turn['turn_name']}: {', '.join(turn['coaching']['strong_points'][:2])}\n"

        return report


# Test
if __name__ == "__main__":
    # Sample data
    sample_df = pd.DataFrame({
        'Sector': np.repeat(range(1, 20), 50),  # 19 turns, 50 points each
        'Speed': np.concatenate([
            np.random.normal(70, 10, 50),   # T1 slow
            np.random.normal(135, 10, 50),  # T2 fast
            np.random.normal(115, 15, 50),  # T3-5 complex
            *[np.random.normal(160, 10, 50) for _ in range(5)],  # T6-10 fast
            np.random.normal(65, 8, 50),    # T11 hairpin
            *[np.random.normal(125, 12, 50) for _ in range(7)],  # T12-18
            np.random.normal(110, 10, 50)   # T19
        ]),
        'BrakePressure': np.random.uniform(0, 100, 950),
        'Throttle': np.random.uniform(0, 100, 950),
        'SteeringAngle': np.random.normal(0, 20, 950)
    })

    coach = TurnCoachingSystem()

    # Test single turn
    print("=== SINGLE TURN TEST ===")
    turn_1_data = sample_df[sample_df['Sector'] == 1]
    analysis = coach.analyze_turn_performance(1, turn_1_data)

    print(f"Turn: {analysis['turn_name']}")
    print(f"Grade: {analysis['grade']}")
    print(f"Min Speed: {analysis['metrics']['min_speed']:.1f} km/h")
    print(f"Primary Issue: {analysis['coaching']['primary_issue']}")
    print("\nRecommendations:")
    for rec in analysis['coaching']['recommendations']:
        print(f"  {rec}")

    # Test all turns
    print("\n\n=== ALL TURNS TEST ===")
    all_analysis = coach.analyze_all_turns(sample_df, sector_column='Sector')
    print(f"Analyzed {len(all_analysis)} turns")

    # Full report
    print("\n" + coach.generate_full_coaching_report())
