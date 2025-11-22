"""
Race Story Generator
AI-powered narrative timeline creation

JÜRI İÇİN STORYTELLING:
Anomaly + events → Natural language race story
Toyota mühendisleri bu hikayeyi okuyarak yarışı anlıyor
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RaceStoryGenerator:
    """
    Yarış hikayesi oluşturucunun race story timeline'ını çıkarıyor
    """

    def __init__(self):
        self.events: List[Dict] = []
        self.story: str = ""

    def extract_key_events(self, df: pd.DataFrame) -> List[Dict]:
        """
        Telemetriden key event'leri çıkar

        Events:
        - Best lap
        - Anomalies
        - Speed peaks
        - Mistakes (lock-up, oversteer)
        - Perfect sectors

        Args:
            df: Telemetry DataFrame

        Returns:
            List of event dicts
        """
        events = []

        # Event 1: Best lap
        if 'LapNumber' in df.columns and 'Speed' in df.columns:
            lap_avg_speeds = df.groupby('LapNumber')['Speed'].mean()
            best_lap = lap_avg_speeds.idxmax()

            events.append({
                'lap': int(best_lap),
                'type': 'best_lap',
                'severity': 'positive',
                'description': f"Best lap achieved",
                'metric': f"{lap_avg_speeds.max():.1f} km/h avg speed"
            })

        # Event 2: Anomalies
        if 'total_anomalies' in df.columns and 'LapNumber' in df.columns:
            anomaly_laps = df[df['total_anomalies'] > 0].groupby('LapNumber')['total_anomalies'].sum()

            for lap, count in anomaly_laps.items():
                if count >= 3:  # Significant anomalies
                    events.append({
                        'lap': int(lap),
                        'type': 'anomaly',
                        'severity': 'negative',
                        'description': f"{int(count)} anomalies detected",
                        'metric': 'Multiple telemetry irregularities'
                    })

        # Event 3: Speed peaks
        if 'Speed' in df.columns and 'LapNumber' in df.columns:
            max_speed_idx = df['Speed'].idxmax()
            max_speed_lap = df.loc[max_speed_idx, 'LapNumber']
            max_speed = df.loc[max_speed_idx, 'Speed']

            events.append({
                'lap': int(max_speed_lap),
                'type': 'speed_peak',
                'severity': 'positive',
                'description': f"Maximum speed reached",
                'metric': f"{max_speed:.1f} km/h"
            })

        # Event 4: Brake pressure spikes
        if 'BrakePressure' in df.columns and 'LapNumber' in df.columns:
            excessive_brake = df[df['BrakePressure'] > 95]

            if len(excessive_brake) > 0:
                brake_laps = excessive_brake.groupby('LapNumber').size()

                for lap, count in brake_laps.items():
                    if count > 5:
                        events.append({
                            'lap': int(lap),
                            'type': 'excessive_braking',
                            'severity': 'warning',
                            'description': f"Over-braking detected",
                            'metric': f"{count} instances >95 bar"
                        })

        # Event 5: Consistency drops
        if 'speed_consistency' in df.columns and 'LapNumber' in df.columns:
            lap_consistency = df.groupby('LapNumber')['speed_consistency'].mean()
            low_consistency_laps = lap_consistency[lap_consistency < 70]

            for lap, score in low_consistency_laps.items():
                events.append({
                    'lap': int(lap),
                    'type': 'inconsistency',
                    'severity': 'warning',
                    'description': f"Consistency drop",
                    'metric': f"{score:.1f}% consistency"
                })

        # Sort by lap
        events.sort(key=lambda x: x['lap'])

        self.events = events
        logger.info(f"Extracted {len(events)} key events")

        return events

    def generate_narrative(self, events: Optional[List[Dict]] = None) -> str:
        """
        Event'lerden natural language hikaye oluştur

        Args:
            events: Event list (None = use self.events)

        Returns:
            Narrative string
        """
        if events is None:
            events = self.events

        if not events:
            return "No significant events detected in this session."

        narrative = "=== RACE STORY ===\n\n"

        # Group events by lap
        laps = {}
        for event in events:
            lap = event['lap']
            if lap not in laps:
                laps[lap] = []
            laps[lap].append(event)

        # Generate narrative per lap
        for lap in sorted(laps.keys()):
            lap_events = laps[lap]

            narrative += f"🏁 LAP {lap}:\n"

            for event in lap_events:
                icon = self._get_event_icon(event['severity'])
                narrative += f"{icon} {event['description']} - {event['metric']}\n"

            narrative += "\n"

        # Summary
        narrative += self._generate_summary(events)

        self.story = narrative
        return narrative

    def _get_event_icon(self, severity: str) -> str:
        """Event severity iconları"""
        icons = {
            'positive': '✅',
            'negative': '❌',
            'warning': '⚠️',
            'neutral': '📊'
        }
        return icons.get(severity, '📌')

    def _generate_summary(self, events: List[Dict]) -> str:
        """
        Hikaye özeti

        Args:
            events: Event list

        Returns:
            Summary string
        """
        summary = "=== SESSION SUMMARY ===\n"

        # Count events by type
        positive = len([e for e in events if e['severity'] == 'positive'])
        negative = len([e for e in events if e['severity'] == 'negative'])
        warnings = len([e for e in events if e['severity'] == 'warning'])

        summary += f"Positive events: {positive}\n"
        summary += f"Issues detected: {negative}\n"
        summary += f"Warnings: {warnings}\n\n"

        # Overall assessment
        if positive > negative + warnings:
            summary += "✅ Overall: Strong performance with minimal issues.\n"
        elif negative > positive:
            summary += "❌ Overall: Multiple issues detected. Focus on consistency.\n"
        else:
            summary += "⚠️ Overall: Mixed performance. Room for improvement.\n"

        return summary

    def get_timeline_data(self) -> pd.DataFrame:
        """
        Timeline visualization için data

        Returns:
            DataFrame with event timeline
        """
        if not self.events:
            return pd.DataFrame()

        timeline_data = []

        for event in self.events:
            timeline_data.append({
                'Lap': event['lap'],
                'Event': event['description'],
                'Type': event['type'],
                'Severity': event['severity'],
                'Details': event['metric']
            })

        return pd.DataFrame(timeline_data)

    def export_to_ai(self) -> str:
        """
        AI Race Engineer için formatted export

        Returns:
            AI-ready context string
        """
        if not self.events:
            return "No race events to report."

        ai_context = "RACE EVENT TIMELINE:\n\n"

        for event in self.events:
            ai_context += f"Lap {event['lap']}: {event['type']} - {event['description']} ({event['metric']})\n"

        ai_context += "\n" + self._generate_summary(self.events)

        return ai_context


# Test
if __name__ == "__main__":
    # Sample data
    sample_df = pd.DataFrame({
        'LapNumber': np.repeat(range(1, 11), 100),
        'Speed': np.random.normal(150, 20, 1000),
        'BrakePressure': np.random.uniform(0, 100, 1000),
        'total_anomalies': np.random.randint(0, 5, 1000),
        'speed_consistency': np.random.uniform(60, 95, 1000)
    })

    generator = RaceStoryGenerator()
    events = generator.extract_key_events(sample_df)

    print(f"Found {len(events)} events\n")
    print(generator.generate_narrative())
    print("\n=== AI EXPORT ===")
    print(generator.export_to_ai())
