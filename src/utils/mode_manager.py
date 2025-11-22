"""
Engineer/Pilot Mode Manager
Dual-level interface for different user expertise

PROFESYONEL ÖZELLİK:
- Pilot Mode: Basit dil, anlaşılır metrikler
- Engineer Mode: Teknik terminoloji, detaylı metrikler
"""

from typing import Dict, Any
import streamlit as st


class ModeManager:
    """
    Interface mode yöneticisi

    Toyota approach:
    - Pilot: Driver-facing, simple language
    - Engineer: TRD engineer-facing, technical
    """

    def __init__(self):
        self.current_mode = "pilot"  # Default: pilot mode

    def set_mode(self, mode: str) -> None:
        """
        Mode değiştir

        Args:
            mode: "pilot" or "engineer"
        """
        if mode.lower() in ["pilot", "engineer"]:
            self.current_mode = mode.lower()

    def get_mode(self) -> str:
        """Current mode"""
        return self.current_mode

    def is_engineer_mode(self) -> bool:
        """Engineer mode aktif mi?"""
        return self.current_mode == "engineer"

    def translate_metric_name(self, metric: str) -> str:
        """
        Metrik isimlerini mode'a göre çevir

        Args:
            metric: Original metric name

        Returns:
            Translated name
        """
        translations = {
            # Pilot Mode → Engineer Mode
            'brake_aggressiveness': {
                'pilot': 'Brake Style',
                'engineer': 'Brake Aggressiveness Index'
            },
            'throttle_smoothness': {
                'pilot': 'Gas Control',
                'engineer': 'Throttle Modulation Coefficient'
            },
            'tire_stress': {
                'pilot': 'Tire Wear',
                'engineer': 'Compound Stress Index'
            },
            'grip_index': {
                'pilot': 'Track Grip',
                'engineer': 'Surface Friction Coefficient'
            },
            'speed_consistency': {
                'pilot': 'Pace Consistency',
                'engineer': 'Velocity Variance Index'
            },
            'turn_entry_quality': {
                'pilot': 'Corner Entry',
                'engineer': 'Trail Braking Efficiency'
            },
            'cpi': {
                'pilot': 'Performance Score',
                'engineer': 'Composite Performance Index'
            },
            'sector_time_loss': {
                'pilot': 'Time Lost',
                'engineer': 'Sector Delta (vs optimal)'
            }
        }

        if metric in translations:
            return translations[metric][self.current_mode]

        return metric

    def get_metric_description(self, metric: str) -> str:
        """
        Metrik açıklaması (mode-specific)

        Args:
            metric: Metric name

        Returns:
            Description text
        """
        descriptions = {
            'brake_aggressiveness': {
                'pilot': 'How hard you brake (higher = more aggressive)',
                'engineer': 'Brake pressure application rate and peak force distribution'
            },
            'throttle_smoothness': {
                'pilot': 'How smooth your gas pedal control is',
                'engineer': 'Throttle position variance and modulation frequency'
            },
            'tire_stress': {
                'pilot': 'How much you\'re wearing your tires',
                'engineer': 'Combined lateral/longitudinal load with thermal degradation factor'
            },
            'grip_index': {
                'pilot': 'How much grip the track has',
                'engineer': 'Temperature-corrected surface adhesion coefficient (μ)'
            },
            'cpi': {
                'pilot': 'Overall lap quality score',
                'engineer': 'Weighted multi-factor performance aggregation (0-100 scale)'
            }
        }

        if metric in descriptions:
            return descriptions[metric][self.current_mode]

        return ""

    def format_value(self, metric: str, value: float) -> str:
        """
        Değerleri mode'a göre formatla

        Args:
            metric: Metric name
            value: Raw value

        Returns:
            Formatted string
        """
        if self.current_mode == "pilot":
            # Basit formatlar
            if metric in ['cpi', 'brake_aggressiveness', 'throttle_smoothness']:
                if value >= 90:
                    return f"{value:.0f} - Excellent"
                elif value >= 75:
                    return f"{value:.0f} - Good"
                elif value >= 60:
                    return f"{value:.0f} - Fair"
                else:
                    return f"{value:.0f} - Needs Work"

            return f"{value:.1f}"

        else:
            # Engineer mode: Daha detaylı
            return f"{value:.3f}"

    def get_recommendation_tone(self, issue: str) -> str:
        """
        Tavsiye dilini mode'a göre ayarla

        Args:
            issue: Issue description

        Returns:
            Mode-appropriate recommendation
        """
        recommendations = {
            'brake_too_early': {
                'pilot': 'Try braking later into the corner',
                'engineer': 'Brake point 8-12m forward. Reduce initial pressure 5-7 bar.'
            },
            'throttle_too_aggressive': {
                'pilot': 'Be smoother with the gas pedal',
                'engineer': 'Reduce throttle application rate. Target 15% linear ramp vs current spike.'
            },
            'high_tire_stress': {
                'pilot': 'You\'re pushing the tires too hard',
                'engineer': 'Compound stress exceeds optimal. Reduce lateral G-load by 0.2G in Turns 4, 7, 12.'
            },
            'inconsistent_laps': {
                'pilot': 'Try to keep your lap times more consistent',
                'engineer': 'Lap-to-lap variance 0.4s. Focus on brake point repeatability ±2m tolerance.'
            }
        }

        if issue in recommendations:
            return recommendations[issue][self.current_mode]

        return issue

    def get_ai_system_prompt_modifier(self) -> str:
        """
        AI Race Engineer için mode-specific prompt

        Returns:
            Prompt modifier string
        """
        if self.current_mode == "pilot":
            return """
Speak in simple, driver-friendly language:
- Avoid technical jargon
- Use analogies and simple explanations
- Focus on actionable advice ("brake later", "smoother throttle")
- Keep responses under 100 words
- Be encouraging and supportive
"""
        else:
            return """
Use professional racing engineer terminology:
- Technical precision required (cite specific values)
- Use engineering terms: oversteer, understeer, brake fade, compound degradation
- Reference specific data points and measurements
- Provide detailed technical analysis
- Expected knowledge: F1/endurance racing engineering
"""

    def get_ui_settings(self) -> Dict[str, Any]:
        """
        UI ayarlarını mode'a göre ver

        Returns:
            Dict with UI settings
        """
        if self.current_mode == "pilot":
            return {
                'show_advanced_metrics': False,
                'chart_complexity': 'simple',
                'metric_precision': 1,  # Decimal places
                'show_raw_data': False,
                'color_scheme': 'friendly',  # Green/Yellow/Red
                'tooltip_detail': 'basic'
            }
        else:
            return {
                'show_advanced_metrics': True,
                'chart_complexity': 'detailed',
                'metric_precision': 3,
                'show_raw_data': True,
                'color_scheme': 'technical',  # Data-driven colors
                'tooltip_detail': 'technical'
            }


# Streamlit integration helper
def render_mode_toggle():
    """
    Streamlit sidebar mode toggle

    Returns:
        ModeManager instance
    """
    if 'mode_manager' not in st.session_state:
        st.session_state.mode_manager = ModeManager()

    manager = st.session_state.mode_manager

    # Sidebar toggle
    with st.sidebar:
        st.divider()
        st.subheader("⚙️ Interface Mode")

        mode = st.radio(
            "Select Mode",
            options=["pilot", "engineer"],
            index=0 if manager.get_mode() == "pilot" else 1,
            format_func=lambda x: "🏎️ Pilot Mode" if x == "pilot" else "🔧 Engineer Mode",
            help="Pilot Mode: Simple language. Engineer Mode: Technical details."
        )

        if mode != manager.get_mode():
            manager.set_mode(mode)
            st.rerun()

        # Mode description
        if mode == "pilot":
            st.caption("📱 Driver-friendly interface with simple explanations")
        else:
            st.caption("🛠️ Technical interface for race engineers")

    return manager


# Test
if __name__ == "__main__":
    manager = ModeManager()

    print("=== MODE MANAGER TEST ===\n")

    # Test both modes
    for mode in ["pilot", "engineer"]:
        manager.set_mode(mode)
        print(f"--- {mode.upper()} MODE ---")

        metric = "brake_aggressiveness"
        print(f"Name: {manager.translate_metric_name(metric)}")
        print(f"Description: {manager.get_metric_description(metric)}")
        print(f"Value format: {manager.format_value(metric, 75.3)}")
        print(f"Recommendation: {manager.get_recommendation_tone('brake_too_early')}")
        print()
