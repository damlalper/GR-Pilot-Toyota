"""
Sector Analysis Page
19-turn detailed weakness map and sector coaching

JÜRI İÇİN KRİTİK: Dataset'in unique kullanımı gösteriliyor
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.styles import apply_custom_css, TOYOTA_COLORS
from analysis.sector_analyzer import SectorAnalyzer
from visualization.charts import create_sector_heatmap


def render():
    """Render sector analysis page"""

    apply_custom_css()

    st.markdown(f"""
    <h1 style="color: {TOYOTA_COLORS['primary_red']};">🗺️ Sector Analysis</h1>
    <p style="color: {TOYOTA_COLORS['text_gray']};">19-Turn detailed performance breakdown</p>
    """, unsafe_allow_html=True)

    # Check if data is loaded
    if st.session_state.get('enriched_df') is None:
        st.warning("⚠️ No data loaded. Please upload a CSV file from the sidebar.")
        return

    df = st.session_state.enriched_df

    # Initialize sector analyzer
    if 'sector_analyzer' not in st.session_state:
        st.session_state.sector_analyzer = SectorAnalyzer()

    analyzer = st.session_state.sector_analyzer

    # Load and analyze sectors
    try:
        with st.spinner("Analyzing 19 sectors..."):
            analyzer.load_sector_data(df)
            sector_results = analyzer.analyze_sector_performance()

    except Exception as e:
        st.error(f"❌ Error loading sector data: {str(e)}")
        st.info("💡 Tip: Make sure your CSV has 'SectorNumber' and 'SectorTime' columns, or 'Distance' and 'LapNumber'.")
        return

    # ===== OVERVIEW METRICS =====
    st.subheader("📊 Sector Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    total_recoverable = analyzer.calculate_total_recoverable_time()
    weaknesses = analyzer.get_weakness_map(top_n=5)
    strengths = analyzer.get_strength_map(top_n=5)

    with col1:
        st.metric(
            "Total Sectors",
            len(sector_results)
        )

    with col2:
        st.metric(
            "Recoverable Time",
            f"{total_recoverable:.3f}s",
            delta="per lap"
        )

    with col3:
        if weaknesses:
            worst_sector, worst_loss = weaknesses[0]
            st.metric(
                "Weakest Sector",
                f"Turn {worst_sector}",
                delta=f"-{worst_loss:.3f}s",
                delta_color="inverse"
            )

    with col4:
        if strengths:
            best_sector, best_consistency = strengths[0]
            st.metric(
                "Strongest Sector",
                f"Turn {best_sector}",
                delta=f"{best_consistency:.1f}%",
                delta_color="normal"
            )

    st.divider()

    # ===== WEAKNESS MAP =====
    st.subheader("🔥 Weakness Map - Top 5 Time Loss Areas")

    weakness_col1, weakness_col2 = st.columns([2, 1])

    with weakness_col1:
        # Heatmap
        heatmap_fig = create_sector_heatmap(sector_results)
        st.plotly_chart(heatmap_fig, use_container_width=True)

    with weakness_col2:
        st.markdown("### 🎯 Priority Sectors")

        for i, (sector, time_loss) in enumerate(weaknesses, 1):
            insight = analyzer.get_sector_insights(sector)

            color = TOYOTA_COLORS['error_red'] if i <= 2 else TOYOTA_COLORS['warning_yellow'] if i <= 4 else TOYOTA_COLORS['text_gray']

            st.markdown(f"""
            <div style="
                background-color: {TOYOTA_COLORS['secondary_bg']};
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid {color};
                margin-bottom: 8px;
            ">
                <h4 style="margin: 0; color: {TOYOTA_COLORS['text_white']};">
                    {i}. Turn {sector}
                </h4>
                <p style="font-size: 1.3rem; font-weight: bold; margin: 5px 0; color: {color};">
                    -{time_loss:.3f}s
                </p>
                <p style="font-size: 0.85rem; color: {TOYOTA_COLORS['text_gray']}; margin: 0;">
                    {insight['priority']} • {insight['consistency_level']} consistency
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ===== TURN-BY-TURN DETAILS =====
    st.subheader("🔍 Turn-by-Turn Analysis")

    # Sector selector
    selected_sector = st.selectbox(
        "Select Turn to Analyze",
        options=list(range(1, 20)),
        format_func=lambda x: f"Turn {x}"
    )

    if selected_sector:
        insight = analyzer.get_sector_insights(selected_sector)
        stats = insight['stats']

        # Sector details
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px;">
                <h3 style="color: {TOYOTA_COLORS['primary_red']};">Turn {selected_sector}</h3>
                <p style="font-size: 0.9rem; color: {TOYOTA_COLORS['text_gray']}; margin: 5px 0;">
                    {insight['performance_level']}
                </p>
                <p style="font-size: 1.1rem; font-weight: bold; color: {TOYOTA_COLORS['text_white']}; margin: 10px 0;">
                    {insight['priority']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric(
                "Average Time",
                f"{stats['avg_time']:.3f}s",
                delta=None
            )
            st.metric(
                "Best Time",
                f"{stats['best_time']:.3f}s",
                delta=None
            )

        with col3:
            st.metric(
                "Time Loss",
                f"{stats['delta_to_best']:.3f}s",
                delta="vs best",
                delta_color="inverse"
            )
            st.metric(
                "Consistency",
                f"{stats['consistency']:.1f}%",
                delta=None
            )

        # Recommendation box
        st.markdown(f"""
        <div style="
            background-color: {TOYOTA_COLORS['secondary_bg']};
            padding: 20px;
            border-radius: 8px;
            border-left: 6px solid {TOYOTA_COLORS['primary_red']};
            margin: 20px 0;
        ">
            <h4 style="color: {TOYOTA_COLORS['primary_red']}; margin: 0 0 10px 0;">
                💡 AI Recommendation
            </h4>
            <p style="color: {TOYOTA_COLORS['text_white']}; font-size: 1.05rem; margin: 0;">
                {insight['recommendation']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Detailed stats
        with st.expander("📊 Detailed Statistics"):
            stats_df = pd.DataFrame([{
                'Metric': 'Average Time',
                'Value': f"{stats['avg_time']:.3f}s"
            }, {
                'Metric': 'Best Time',
                'Value': f"{stats['best_time']:.3f}s"
            }, {
                'Metric': 'Worst Time',
                'Value': f"{stats['worst_time']:.3f}s"
            }, {
                'Metric': 'Standard Deviation',
                'Value': f"{stats['std_dev']:.3f}s"
            }, {
                'Metric': 'Consistency Score',
                'Value': f"{stats['consistency']:.1f}%"
            }, {
                'Metric': 'Potential Gain',
                'Value': f"{stats['potential_gain']:.3f}s"
            }, {
                'Metric': 'Attempts',
                'Value': stats['attempts']
            }])

            if stats['avg_speed']:
                stats_df = pd.concat([stats_df, pd.DataFrame([{
                    'Metric': 'Average Speed',
                    'Value': f"{stats['avg_speed']:.1f} km/h"
                }, {
                    'Metric': 'Min Speed',
                    'Value': f"{stats['min_speed']:.1f} km/h"
                }, {
                    'Metric': 'Max Speed',
                    'Value': f"{stats['max_speed']:.1f} km/h"
                }])], ignore_index=True)

            st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.divider()

    # ===== FULL SECTOR REPORT =====
    st.subheader("📋 Full Sector Report")

    report_df = analyzer.export_sector_report()

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True,
        height=600
    )

    # Download button
    csv = report_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Sector Report (CSV)",
        data=csv,
        file_name='sector_analysis_report.csv',
        mime='text/csv',
        help="Download complete sector analysis report"
    )

    st.divider()

    # ===== AI COACHING SUMMARY =====
    st.subheader("🤖 AI Coaching Summary")

    coaching_summary = analyzer.generate_coaching_summary()

    st.text_area(
        "Coaching Summary (Copy to AI Engineer)",
        value=coaching_summary,
        height=200,
        help="This summary can be used with AI Race Engineer for detailed recommendations"
    )

    if st.button("📤 Send to AI Engineer"):
        st.session_state.ai_context_from_sectors = coaching_summary
        st.success("✅ Summary sent to AI Engineer context!")


if __name__ == "__main__":
    render()
