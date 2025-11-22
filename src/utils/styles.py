"""
Toyota GR Design System
Merkezi stil yönetimi ve custom CSS injection
"""

import streamlit as st

TOYOTA_COLORS = {
    'primary_red': '#FF0000',
    'dark_bg': '#0E1117',
    'secondary_bg': '#262730',
    'text_white': '#FAFAFA',
    'text_gray': '#A0A0A0',
    'success_green': '#00D26A',
    'warning_yellow': '#FFD600',
    'error_red': '#FF4B4B',
    'info_blue': '#0066CC'
}

def apply_custom_css():
    """
    Global CSS injection for Toyota GR branding
    Dark mode theme with racing aesthetics
    """
    st.markdown(f"""
    <style>
        /* ===== GLOBAL THEME ===== */
        .stApp {{
            background-color: {TOYOTA_COLORS['dark_bg']};
        }}

        /* ===== TYPOGRAPHY ===== */
        h1 {{
            color: {TOYOTA_COLORS['primary_red']};
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 1rem;
        }}

        h2 {{
            color: {TOYOTA_COLORS['text_white']};
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}

        h3 {{
            color: {TOYOTA_COLORS['text_white']};
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            font-weight: 500;
        }}

        p, li, span {{
            color: {TOYOTA_COLORS['text_white']};
            font-size: 1rem;
            line-height: 1.6;
        }}

        /* ===== METRIC CARDS ===== */
        div[data-testid="metric-container"] {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-left: 4px solid {TOYOTA_COLORS['primary_red']};
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease;
        }}

        div[data-testid="metric-container"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.2);
        }}

        div[data-testid="metric-container"] label {{
            color: {TOYOTA_COLORS['text_gray']};
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
            color: {TOYOTA_COLORS['text_white']};
            font-size: 2rem;
            font-weight: 700;
        }}

        /* ===== BUTTONS ===== */
        .stButton > button {{
            background-color: {TOYOTA_COLORS['primary_red']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .stButton > button:hover {{
            background-color: #CC0000;
            box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3);
            transform: translateY(-1px);
        }}

        .stButton > button:active {{
            transform: translateY(0);
            box-shadow: 0 2px 6px rgba(255, 0, 0, 0.2);
        }}

        /* ===== DATAFRAMES ===== */
        .dataframe {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-radius: 8px;
            overflow: hidden;
        }}

        .dataframe th {{
            background-color: {TOYOTA_COLORS['primary_red']};
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.875rem;
            padding: 12px;
        }}

        .dataframe td {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            color: {TOYOTA_COLORS['text_white']};
            padding: 10px;
            border-bottom: 1px solid {TOYOTA_COLORS['dark_bg']};
        }}

        /* ===== CHARTS ===== */
        .plotly-graph-div {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-radius: 8px;
            padding: 10px;
        }}

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-right: 1px solid {TOYOTA_COLORS['dark_bg']};
        }}

        section[data-testid="stSidebar"] .stRadio > label {{
            color: {TOYOTA_COLORS['text_white']};
            font-weight: 600;
        }}

        /* ===== FILE UPLOADER ===== */
        .uploadedFile {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border: 2px dashed {TOYOTA_COLORS['primary_red']};
            border-radius: 8px;
        }}

        /* ===== DIVIDER ===== */
        hr {{
            border-color: {TOYOTA_COLORS['primary_red']};
            opacity: 0.3;
        }}

        /* ===== INFO/WARNING/ERROR BOXES ===== */
        .stAlert {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-radius: 8px;
            padding: 1rem;
        }}

        div[data-testid="stMarkdownContainer"] > div[data-testid="stAlert"] {{
            border-left: 4px solid {TOYOTA_COLORS['info_blue']};
        }}

        /* ===== HIDE STREAMLIT BRANDING ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* ===== CUSTOM SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {TOYOTA_COLORS['dark_bg']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {TOYOTA_COLORS['primary_red']};
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #CC0000;
        }}

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-radius: 4px 4px 0 0;
            color: {TOYOTA_COLORS['text_gray']};
            font-weight: 600;
            padding: 10px 20px;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {TOYOTA_COLORS['primary_red']};
            color: white;
        }}

        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-radius: 8px;
            font-weight: 600;
            color: {TOYOTA_COLORS['text_white']};
        }}

        .streamlit-expanderHeader:hover {{
            background-color: {TOYOTA_COLORS['primary_red']};
        }}

        /* ===== SELECTBOX & MULTISELECT ===== */
        .stSelectbox, .stMultiSelect {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
        }}

        /* ===== SLIDER ===== */
        .stSlider {{
            padding: 1rem 0;
        }}

        .stSlider [data-baseweb="slider"] {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
        }}

        .stSlider [data-testid="stTickBar"] > div {{
            background-color: {TOYOTA_COLORS['primary_red']};
        }}

        /* ===== CUSTOM BADGE ===== */
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-success {{
            background-color: {TOYOTA_COLORS['success_green']};
            color: white;
        }}

        .badge-warning {{
            background-color: {TOYOTA_COLORS['warning_yellow']};
            color: {TOYOTA_COLORS['dark_bg']};
        }}

        .badge-error {{
            background-color: {TOYOTA_COLORS['error_red']};
            color: white;
        }}

        .badge-info {{
            background-color: {TOYOTA_COLORS['info_blue']};
            color: white;
        }}

        /* ===== LOADING SPINNER ===== */
        .stSpinner > div {{
            border-top-color: {TOYOTA_COLORS['primary_red']};
        }}

        /* ===== CODE BLOCKS ===== */
        code {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            color: {TOYOTA_COLORS['primary_red']};
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}

        pre {{
            background-color: {TOYOTA_COLORS['secondary_bg']};
            border-left: 4px solid {TOYOTA_COLORS['primary_red']};
            padding: 1rem;
            border-radius: 4px;
        }}
    </style>
    """, unsafe_allow_html=True)


def create_badge(text: str, badge_type: str = 'info') -> str:
    """
    Create a styled badge HTML

    Args:
        text: Badge text
        badge_type: 'success', 'warning', 'error', or 'info'

    Returns:
        HTML string for badge
    """
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def create_header_with_logo(title: str, subtitle: str = None) -> None:
    """
    Create a header with Toyota GR branding

    Args:
        title: Main title
        subtitle: Optional subtitle
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title(title)
        if subtitle:
            st.caption(subtitle)

    with col2:
        # Logo placeholder - replace with actual Toyota GR logo
        st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <div style="
                background-color: {TOYOTA_COLORS['primary_red']};
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 1.5rem;
                letter-spacing: 2px;
            ">
                GR
            </div>
        </div>
        """, unsafe_allow_html=True)
