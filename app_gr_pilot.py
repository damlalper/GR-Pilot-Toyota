"""
GR-Pilot - Toyota Race Engineering Assistant
Main Streamlit Application

🏎️ AI-Powered Post-Race Analysis Dashboard
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.styles import apply_custom_css, create_header_with_logo, TOYOTA_COLORS
from utils.data_loader import DataManager
from analysis.telemetry_fusion import TelemetryFusionEngine
from analysis.cpi_calculator import CompositePerformanceIndex
from visualization.charts import (
    create_lap_time_evolution,
    create_speed_trace,
    create_cpi_breakdown_chart,
    create_cpi_trend,
    create_performance_gauge
)

# Page config
st.set_page_config(
    page_title="GR-Pilot | Toyota Race Engineering",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager(data_dir="data")

if 'fusion_engine' not in st.session_state:
    st.session_state.fusion_engine = TelemetryFusionEngine()

if 'cpi_calculator' not in st.session_state:
    st.session_state.cpi_calculator = CompositePerformanceIndex()

if 'enriched_df' not in st.session_state:
    st.session_state.enriched_df = None


# ===== SIDEBAR =====
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div style="
            background: linear-gradient(135deg, {TOYOTA_COLORS['primary_red']} 0%, #CC0000 100%);
            color: white;
            padding: 15px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 2rem;
            letter-spacing: 3px;
            box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
        ">
            GR PILOT
        </div>
        <p style="color: {TOYOTA_COLORS['text_gray']}; margin-top: 10px; font-size: 0.9rem;">
            AI Race Engineering Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📊 Telemetry Analysis",
            "🗺️ Sector Analysis",
            "🤖 AI Race Engineer",
            "📈 Performance Index (CPI)",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    # Data Upload
    st.subheader("📁 Data Upload")

    uploaded_file = st.file_uploader(
        "Upload Race Telemetry",
        type=['csv'],
        help="Upload any CSV file (telemetry, lap times, weather, etc.)"
    )

    if uploaded_file:
        with st.spinner("Loading data..."):
            try:
                df, filename = st.session_state.data_manager.load_from_upload(uploaded_file)

                st.success(f"✅ Loaded: {filename}")
                st.caption(f"{len(df):,} rows × {len(df.columns)} columns")

                # Add to fusion engine
                st.session_state.fusion_engine.add_dataset(filename, df)

                # Feature engineering
                with st.spinner("Engineering features..."):
                    enriched_df = st.session_state.fusion_engine.engineer_features(df)
                    enriched_df = st.session_state.fusion_engine.detect_anomalies(enriched_df)
                    st.session_state.enriched_df = enriched_df

                st.success("✅ Feature engineering complete!")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    st.divider()

    # Quick Stats
    if st.session_state.enriched_df is not None:
        st.subheader("📊 Quick Stats")

        df = st.session_state.enriched_df

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Data Points",
                f"{len(df):,}"
            )

        with col2:
            if 'LapNumber' in df.columns:
                st.metric(
                    "Total Laps",
                    int(df['LapNumber'].max())
                )

        if 'total_anomalies' in df.columns:
            anomaly_count = int(df['total_anomalies'].sum())
            st.metric(
                "Anomalies",
                anomaly_count,
                delta=f"{anomaly_count/len(df)*100:.1f}%" if len(df) > 0 else "0%"
            )


# ===== MAIN CONTENT =====

if page == "🏠 Overview":
    create_header_with_logo(
        "GR-Pilot Dashboard",
        "Session Overview & Critical Insights"
    )

    if st.session_state.enriched_df is None:
        st.info("👈 Please upload a telemetry CSV file from the sidebar to begin analysis.")

        st.markdown("### 🚀 Features")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px; border-left: 4px solid {TOYOTA_COLORS['primary_red']};">
                <h4>📊 Multi-Dataset Fusion</h4>
                <p style="color: {TOYOTA_COLORS['text_gray']};">
                    Combines telemetry, weather, and sector data into unified analysis
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px; border-left: 4px solid {TOYOTA_COLORS['primary_red']};">
                <h4>🤖 AI Race Engineer</h4>
                <p style="color: {TOYOTA_COLORS['text_gray']};">
                    GPT-4 powered natural language coaching and recommendations
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px; border-left: 4px solid {TOYOTA_COLORS['primary_red']};">
                <h4>📈 Performance Index</h4>
                <p style="color: {TOYOTA_COLORS['text_gray']};">
                    Single metric (0-100) combining 6 performance factors
                </p>
            </div>
            """, unsafe_allow_html=True)

    else:
        df = st.session_state.enriched_df

        # Hero Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if 'Speed' in df.columns:
                avg_speed = df['Speed'].mean()
                st.metric(
                    "Avg Speed",
                    f"{avg_speed:.1f} km/h",
                    delta=None
                )

        with col2:
            if 'LapNumber' in df.columns:
                # Calculate overall CPI
                overall_cpi = st.session_state.cpi_calculator.calculate_cpi(df)
                st.metric(
                    "Overall CPI",
                    f"{overall_cpi['total_cpi']}/100",
                    delta=overall_cpi['grade']
                )

        with col3:
            if 'total_anomalies' in df.columns:
                critical_issues = int(df[df['total_anomalies'] >= 2].shape[0])
                st.metric(
                    "Critical Issues",
                    critical_issues,
                    delta="data points"
                )

        with col4:
            if 'brake_efficiency' in df.columns:
                avg_brake_eff = df['brake_efficiency'].mean()
                st.metric(
                    "Brake Efficiency",
                    f"{avg_brake_eff:.1f}%",
                    delta=None
                )

        st.divider()

        # Lap Time Evolution Chart
        if 'LapNumber' in df.columns:
            st.subheader("🏁 Lap Time Evolution")
            lap_time_fig = create_lap_time_evolution(df)
            st.plotly_chart(lap_time_fig, use_container_width=True)

            st.divider()

        # Speed Trace
        if 'Speed' in df.columns:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("🏎️ Speed Trace")
                speed_fig = create_speed_trace(df)
                st.plotly_chart(speed_fig, use_container_width=True)

            with col2:
                st.subheader("📊 Session Stats")
                st.metric("Total Laps", int(df['LapNumber'].max()) if 'LapNumber' in df.columns else "N/A")
                st.metric("Avg Speed", f"{df['Speed'].mean():.1f} km/h")
                st.metric("Max Speed", f"{df['Speed'].max():.1f} km/h")

                if 'speed_consistency' in df.columns:
                    st.metric("Consistency", f"{df['speed_consistency'].mean():.1f}/100")

            st.divider()

        # Data Preview
        st.subheader("📋 Data Preview")

        with st.expander("View Raw Data", expanded=False):
            st.dataframe(
                df.head(100),
                use_container_width=True
            )

        # Feature Summary
        if st.session_state.fusion_engine.feature_engineered_df is not None:
            st.subheader("🔬 Engineered Features")

            feature_summary = st.session_state.fusion_engine.get_feature_summary()

            if feature_summary:
                summary_df = pd.DataFrame(feature_summary).T
                st.dataframe(
                    summary_df.style.format("{:.2f}"),
                    use_container_width=True
                )


elif page == "📊 Telemetry Analysis":
    # Import and render telemetry page
    from pages import telemetry_analysis
    telemetry_analysis.render()


elif page == "🗺️ Sector Analysis":
    # Import and render sector analysis page
    from pages import sector_analysis_page
    sector_analysis_page.render()


elif page == "🤖 AI Race Engineer":
    # Import and render AI engineer page
    from pages import ai_engineer_page
    ai_engineer_page.render()


elif page == "📈 Performance Index (CPI)":
    create_header_with_logo(
        "Composite Performance Index",
        "Single metric combining 6 performance factors"
    )

    if st.session_state.enriched_df is None:
        st.warning("⚠️ No data loaded. Please upload a CSV file.")
    else:
        df = st.session_state.enriched_df

        # Calculate CPI
        cpi_result = st.session_state.cpi_calculator.calculate_cpi(df)

        # Display CPI with Gauge
        col1, col2 = st.columns([1, 1])

        with col1:
            # Performance Gauge
            gauge_fig = create_performance_gauge(cpi_result['total_cpi'])
            st.plotly_chart(gauge_fig, use_container_width=True)

        with col2:
            st.markdown(f"""
            <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 30px; border-radius: 12px; border-left: 6px solid {TOYOTA_COLORS['primary_red']}; height: 350px; display: flex; flex-direction: column; justify-content: center;">
                <h1 style="color: {TOYOTA_COLORS['primary_red']}; font-size: 4rem; margin: 0; text-align: center;">{cpi_result['total_cpi']}</h1>
                <h3 style="color: {TOYOTA_COLORS['text_white']}; margin: 10px 0; text-align: center;">Grade: {cpi_result['grade']}</h3>
                <p style="color: {TOYOTA_COLORS['text_gray']}; text-align: center; font-size: 1.1rem;">{cpi_result['interpretation']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # CPI Breakdown Charts
        col1, col2 = st.columns([1, 1])

        with col1:
            # Radar chart
            breakdown_fig = create_cpi_breakdown_chart(cpi_result)
            st.plotly_chart(breakdown_fig, use_container_width=True)

        with col2:
            # Breakdown table
            st.subheader("📊 Component Scores")

            breakdown_df = pd.DataFrame([cpi_result['breakdown']]).T
            breakdown_df.columns = ['Score']

            st.dataframe(
                breakdown_df.style.format("{:.1f}").background_gradient(cmap='RdYlGn', vmin=0, vmax=100),
                use_container_width=True,
                height=400
            )

        st.divider()

        # Lap-by-lap CPI (if lap data available)
        if 'LapNumber' in df.columns:
            st.subheader("📈 CPI Trend Across Laps")

            with st.spinner("Calculating CPI for all laps..."):
                all_lap_cpis = st.session_state.cpi_calculator.calculate_all_laps(df)

            # CPI trend chart
            cpi_trend_fig = create_cpi_trend(all_lap_cpis)
            st.plotly_chart(cpi_trend_fig, use_container_width=True)

            # Best/worst laps
            col1, col2 = st.columns(2)

            best_lap, best_result = st.session_state.cpi_calculator.get_best_lap(df)
            worst_lap, worst_result = st.session_state.cpi_calculator.get_worst_lap(df)

            with col1:
                st.markdown(f"""
                <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px; border-left: 4px solid {TOYOTA_COLORS['success_green']};">
                    <h3 style="color: {TOYOTA_COLORS['success_green']};">🏆 Best Lap</h3>
                    <h1 style="color: {TOYOTA_COLORS['text_white']}; margin: 10px 0;">Lap {best_lap}</h1>
                    <p style="color: {TOYOTA_COLORS['text_white']}; font-size: 1.5rem;">CPI: {best_result['total_cpi']}/100</p>
                    <p style="color: {TOYOTA_COLORS['text_gray']};">Grade: {best_result['grade']}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px; border-left: 4px solid {TOYOTA_COLORS['error_red']};">
                    <h3 style="color: {TOYOTA_COLORS['error_red']};">⚠️ Worst Lap</h3>
                    <h1 style="color: {TOYOTA_COLORS['text_white']}; margin: 10px 0;">Lap {worst_lap}</h1>
                    <p style="color: {TOYOTA_COLORS['text_white']}; font-size: 1.5rem;">CPI: {worst_result['total_cpi']}/100</p>
                    <p style="color: {TOYOTA_COLORS['text_gray']};">Grade: {worst_result['grade']}</p>
                </div>
                """, unsafe_allow_html=True)


elif page == "⚙️ Settings":
    create_header_with_logo(
        "Settings",
        "Configure GR-Pilot preferences"
    )

    st.subheader("🎨 Theme")
    st.info("Dark mode with Toyota GR branding is active")

    st.divider()

    st.subheader("🤖 AI Configuration")

    ai_provider = st.selectbox(
        "AI Provider",
        ["OpenAI GPT-4", "Groq Mixtral"],
        help="Select AI model for race engineering assistant"
    )

    st.text_input(
        "API Key",
        type="password",
        help="Enter your API key (will be stored in session only)"
    )

    st.divider()

    st.subheader("ℹ️ About")

    st.markdown("""
    **GR-Pilot v1.0**

    AI-Powered Race Engineering Assistant for Toyota Gazoo Racing

    Created for Hack the Track 2024

    ---

    **Features:**
    - Multi-dataset fusion
    - Composite Performance Index (CPI)
    - AI Race Engineer
    - Telemetry analysis
    - Feature engineering

    **Tech Stack:**
    - Python 3.11+
    - Streamlit
    - Pandas, NumPy, SciPy
    - OpenAI GPT-4 / Groq
    - Plotly

    ---

    Made with ❤️ for Toyota TRD
    """)


# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: {TOYOTA_COLORS['text_gray']};'>"
    "GR-Pilot © 2024 | Toyota Gazoo Racing | Hack the Track"
    "</div>",
    unsafe_allow_html=True
)
