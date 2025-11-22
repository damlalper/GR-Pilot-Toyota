"""
Telemetry Analysis Page
Detailed telemetry visualization and analysis
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.styles import apply_custom_css, TOYOTA_COLORS
from visualization.charts import (
    create_speed_trace,
    create_telemetry_overlay,
    create_anomaly_timeline
)


def render():
    """Render telemetry analysis page"""

    apply_custom_css()

    st.markdown(f"""
    <h1 style="color: {TOYOTA_COLORS['primary_red']};">📊 Telemetry Analysis</h1>
    <p style="color: {TOYOTA_COLORS['text_gray']};">Detailed multi-channel telemetry visualization</p>
    """, unsafe_allow_html=True)

    # Check if data is loaded
    if st.session_state.get('enriched_df') is None:
        st.warning("⚠️ No data loaded. Please upload a CSV file from the sidebar.")
        return

    df = st.session_state.enriched_df

    # ===== LAP SELECTOR =====
    st.subheader("🎯 Lap Selector")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if 'LapNumber' in df.columns:
            available_laps = sorted(df['LapNumber'].unique())
            selected_lap = st.selectbox(
                "Select Lap",
                options=['All Laps'] + [f'Lap {int(lap)}' for lap in available_laps],
                index=0
            )

            if selected_lap == 'All Laps':
                lap_num = None
                display_df = df
            else:
                lap_num = int(selected_lap.split()[1])
                display_df = df[df['LapNumber'] == lap_num]
        else:
            st.info("No lap information available. Showing all data.")
            lap_num = None
            display_df = df

    with col2:
        # Channel selector
        available_channels = ['Speed', 'BrakePressure', 'Throttle', 'SteeringAngle']
        available_channels = [ch for ch in available_channels if ch in df.columns]

        selected_channels = st.multiselect(
            "Channels to Display",
            options=available_channels,
            default=available_channels[:3] if len(available_channels) >= 3 else available_channels
        )

    with col3:
        st.metric(
            "Data Points",
            f"{len(display_df):,}"
        )

    st.divider()

    # ===== SPEED TRACE =====
    if 'Speed' in df.columns:
        st.subheader("🏎️ Speed Trace")

        speed_fig = create_speed_trace(df, lap_num=lap_num)
        st.plotly_chart(speed_fig, use_container_width=True)

        # Speed statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Avg Speed",
                f"{display_df['Speed'].mean():.1f} km/h"
            )

        with col2:
            st.metric(
                "Max Speed",
                f"{display_df['Speed'].max():.1f} km/h"
            )

        with col3:
            st.metric(
                "Min Speed",
                f"{display_df['Speed'].min():.1f} km/h"
            )

        with col4:
            st.metric(
                "Std Dev",
                f"{display_df['Speed'].std():.1f} km/h"
            )

        st.divider()

    # ===== MULTI-CHANNEL OVERLAY =====
    if selected_channels:
        st.subheader("📈 Multi-Channel Telemetry")

        overlay_fig = create_telemetry_overlay(
            df,
            channels=selected_channels,
            lap_num=lap_num
        )
        st.plotly_chart(overlay_fig, use_container_width=True)

        st.divider()

    # ===== ANOMALY TIMELINE =====
    if 'total_anomalies' in df.columns:
        st.subheader("⚠️ Anomaly Detection")

        anomaly_fig = create_anomaly_timeline(display_df)
        st.plotly_chart(anomaly_fig, use_container_width=True)

        # Anomaly statistics
        total_anomalies = int(display_df['total_anomalies'].sum())
        anomaly_percentage = (total_anomalies / len(display_df) * 100) if len(display_df) > 0 else 0

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Anomalies",
                total_anomalies
            )

        with col2:
            st.metric(
                "Anomaly Rate",
                f"{anomaly_percentage:.2f}%"
            )

        with col3:
            # Find most problematic area
            if 'Speed_anomaly' in df.columns:
                speed_anomalies = int(display_df['Speed_anomaly'].sum())
                st.metric(
                    "Speed Anomalies",
                    speed_anomalies
                )

        st.divider()

    # ===== FEATURE STATISTICS =====
    st.subheader("🔬 Engineered Features")

    feature_cols = [
        'brake_efficiency', 'throttle_smoothness', 'tire_stress',
        'turn_entry_quality', 'speed_consistency', 'g_force_magnitude'
    ]

    available_features = [col for col in feature_cols if col in display_df.columns]

    if available_features:
        # Create metrics grid
        n_cols = 3
        cols = st.columns(n_cols)

        for i, feature in enumerate(available_features):
            with cols[i % n_cols]:
                avg_value = display_df[feature].mean()
                min_value = display_df[feature].min()
                max_value = display_df[feature].max()

                # Format feature name
                feature_name = feature.replace('_', ' ').title()

                st.markdown(f"""
                <div style="
                    background-color: {TOYOTA_COLORS['secondary_bg']};
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid {TOYOTA_COLORS['primary_red']};
                    margin-bottom: 10px;
                ">
                    <h4 style="margin: 0; color: {TOYOTA_COLORS['text_white']};">{feature_name}</h4>
                    <p style="font-size: 2rem; font-weight: bold; margin: 10px 0; color: {TOYOTA_COLORS['primary_red']};">
                        {avg_value:.1f}
                    </p>
                    <p style="font-size: 0.85rem; color: {TOYOTA_COLORS['text_gray']}; margin: 0;">
                        Range: {min_value:.1f} - {max_value:.1f}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

    # ===== RAW DATA PREVIEW =====
    st.subheader("📋 Raw Data Preview")

    # Column selector for raw data
    all_columns = display_df.columns.tolist()

    selected_columns_preview = st.multiselect(
        "Select columns to preview",
        options=all_columns,
        default=all_columns[:8] if len(all_columns) >= 8 else all_columns
    )

    if selected_columns_preview:
        st.dataframe(
            display_df[selected_columns_preview].head(100),
            use_container_width=True,
            height=300
        )

        # Download button
        csv = display_df[selected_columns_preview].to_csv(index=False)
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f'telemetry_lap_{lap_num if lap_num else "all"}.csv',
            mime='text/csv',
            help="Download filtered telemetry data"
        )


if __name__ == "__main__":
    render()
