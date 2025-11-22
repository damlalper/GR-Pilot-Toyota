"""
AI Race Engineer Chat Page
Natural language race engineering assistant
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.styles import apply_custom_css, TOYOTA_COLORS
from ai.race_engineer import AIRaceEngineer


def render():
    """Render AI Race Engineer page"""

    apply_custom_css()

    st.markdown(f"""
    <h1 style="color: {TOYOTA_COLORS['primary_red']};">🤖 AI Race Engineer</h1>
    <p style="color: {TOYOTA_COLORS['text_gray']};">Natural language race engineering assistant powered by GPT-4</p>
    """, unsafe_allow_html=True)

    # ===== API KEY CONFIGURATION =====
    if 'ai_engineer' not in st.session_state:
        st.info("👈 Please configure your API key in the sidebar to activate AI Engineer.")

        with st.sidebar:
            st.subheader("🔑 AI Configuration")

            api_provider = st.selectbox(
                "AI Provider",
                ["OpenAI GPT-4", "Groq Mixtral"],
                help="Select your preferred AI provider"
            )

            api_key = st.text_input(
                "API Key",
                type="password",
                help="Enter your API key"
            )

            if st.button("🚀 Activate AI Engineer"):
                if not api_key:
                    st.error("❌ Please enter an API key")
                else:
                    try:
                        provider = "openai" if "OpenAI" in api_provider else "groq"
                        engineer = AIRaceEngineer(api_key=api_key, provider=provider)
                        st.session_state.ai_engineer = engineer
                        st.success("✅ AI Engineer activated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        return

    # ===== CHAT INTERFACE =====
    engineer = st.session_state.ai_engineer

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Pre-defined questions
    st.subheader("💡 Quick Questions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏁 Why am I slow in Turn 7?", use_container_width=True):
            st.session_state.quick_question = "Why am I slow in Turn 7? Analyze my braking and throttle application."

    with col2:
        if st.button("🔧 Setup recommendations?", use_container_width=True):
            st.session_state.quick_question = "Based on my telemetry, what setup changes would you recommend?"

    with col3:
        if st.button("🏎️ How to improve lap time?", use_container_width=True):
            st.session_state.quick_question = "What are the top 3 areas where I'm losing time? Provide specific recommendations."

    st.divider()

    # Chat container
    st.subheader("💬 Chat with AI Engineer")

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="
                    background-color: {TOYOTA_COLORS['primary_red']};
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    margin-left: 20%;
                ">
                    <p style="margin: 0; color: white;"><b>You:</b></p>
                    <p style="margin: 5px 0 0 0; color: white;">{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background-color: {TOYOTA_COLORS['secondary_bg']};
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    margin-right: 20%;
                    border-left: 4px solid {TOYOTA_COLORS['primary_red']};
                ">
                    <p style="margin: 0; color: {TOYOTA_COLORS['primary_red']};"><b>🤖 AI Engineer:</b></p>
                    <p style="margin: 5px 0 0 0; color: {TOYOTA_COLORS['text_white']};">{message['content']}</p>
                </div>
                """, unsafe_allow_html=True)

    # User input
    st.divider()

    # Check for quick question
    default_question = ""
    if 'quick_question' in st.session_state:
        default_question = st.session_state.quick_question
        del st.session_state.quick_question

    user_input = st.text_area(
        "Ask your question:",
        value=default_question,
        height=100,
        placeholder="Example: Why am I losing time in sector 3? What should I change with my braking?"
    )

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        send_button = st.button("🚀 Send", type="primary", use_container_width=True)

    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            engineer.clear_history()
            st.rerun()

    # Process input
    if send_button and user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        # Prepare context if data is loaded
        context = None
        if st.session_state.get('enriched_df') is not None:
            df = st.session_state.enriched_df

            # Build context from data
            context = {
                'metrics': {}
            }

            if 'Speed' in df.columns:
                context['metrics']['avg_speed'] = float(df['Speed'].mean())
                context['metrics']['max_speed'] = float(df['Speed'].max())

            if 'BrakePressure' in df.columns:
                context['metrics']['avg_brake_pressure'] = float(df['BrakePressure'].mean())

            if 'Throttle' in df.columns:
                context['metrics']['avg_throttle'] = float(df['Throttle'].mean())

            if 'brake_efficiency' in df.columns:
                context['metrics']['brake_efficiency'] = float(df['brake_efficiency'].mean())

            if 'throttle_smoothness' in df.columns:
                context['metrics']['throttle_smoothness'] = float(df['throttle_smoothness'].mean())

            if 'tire_stress' in df.columns:
                context['metrics']['tire_stress'] = float(df['tire_stress'].mean())

            if 'total_anomalies' in df.columns:
                context['anomalies'] = int(df['total_anomalies'].sum())

            # Add CPI if available
            if st.session_state.get('cpi_calculator'):
                try:
                    cpi_result = st.session_state.cpi_calculator.calculate_cpi(df)
                    context['cpi'] = cpi_result['total_cpi']
                except:
                    pass

        # Get AI response
        with st.spinner("🤖 AI Engineer is analyzing..."):
            try:
                response = engineer.analyze(user_input, context=context)

                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error getting AI response: {str(e)}")

    # ===== SIDEBAR INFO =====
    with st.sidebar:
        st.divider()

        st.subheader("ℹ️ AI Engineer Info")

        st.markdown(f"""
        **Provider:** {engineer.provider.title()}

        **Model:** {engineer.model}

        **Conversation Length:** {len(st.session_state.chat_history)} messages

        **Expertise:**
        - Telemetry analysis
        - Driver coaching
        - Setup recommendations
        - Sector analysis
        - Lap time optimization
        """)

        if st.button("🔄 Restart AI Engine"):
            if 'ai_engineer' in st.session_state:
                del st.session_state.ai_engineer
            st.session_state.chat_history = []
            st.rerun()

    # ===== EXAMPLE QUERIES =====
    if not st.session_state.chat_history:
        st.divider()

        st.markdown(f"""
        <div style="background-color: {TOYOTA_COLORS['secondary_bg']}; padding: 20px; border-radius: 8px;">
            <h3 style="color: {TOYOTA_COLORS['primary_red']};">💡 Example Questions</h3>

            <p style="color: {TOYOTA_COLORS['text_white']};"><b>Performance Analysis:</b></p>
            <ul style="color: {TOYOTA_COLORS['text_gray']};">
                <li>"Why am I losing 0.8 seconds in Turn 7?"</li>
                <li>"What's causing my inconsistent lap times?"</li>
                <li>"Analyze my braking points in sector 2"</li>
            </ul>

            <p style="color: {TOYOTA_COLORS['text_white']};"><b>Driver Coaching:</b></p>
            <ul style="color: {TOYOTA_COLORS['text_gray']};">
                <li>"How can I improve my trail braking?"</li>
                <li>"What's the optimal throttle application through Turn 12?"</li>
                <li>"Give me 3 specific areas to focus on for my next session"</li>
            </ul>

            <p style="color: {TOYOTA_COLORS['text_white']};"><b>Setup Recommendations:</b></p>
            <ul style="color: {TOYOTA_COLORS['text_gray']};">
                <li>"Should I increase front wing angle based on my understeer?"</li>
                <li>"What tire pressure changes would help with my pace?"</li>
                <li>"Recommend brake balance adjustments for Turn 7"</li>
            </ul>

            <p style="color: {TOYOTA_COLORS['text_white']};"><b>Race Strategy:</b></p>
            <ul style="color: {TOYOTA_COLORS['text_gray']};">
                <li>"When should I pit based on my tire degradation?"</li>
                <li>"How can I save fuel without losing lap time?"</li>
                <li>"What's my optimal pace for a 20-lap stint?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    render()
