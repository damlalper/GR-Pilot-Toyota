"""
AI Avatar Component for GR-Pilot Toyota Assistant
Creates an animated avatar that speaks with TTS
"""
import streamlit as st
import base64
from pathlib import Path

def create_toyota_avatar_css():
    """Creates CSS for Toyota-themed animated avatar"""
    return """
    <style>
    .avatar-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 20px 0;
        padding: 20px;
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 20px;
        border: 3px solid #EB0A1E;
        box-shadow: 0 8px 32px rgba(235, 10, 30, 0.3);
    }

    .avatar-circle {
        position: relative;
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #EB0A1E 0%, #B00000 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(235, 10, 30, 0.5);
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }

    .avatar-circle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 30px rgba(235, 10, 30, 0.7);
    }

    .avatar-icon {
        font-size: 60px;
        color: white;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }

    .avatar-speaking {
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            box-shadow: 0 4px 20px rgba(235, 10, 30, 0.5);
        }
        50% {
            transform: scale(1.1);
            box-shadow: 0 8px 40px rgba(235, 10, 30, 0.8);
        }
    }

    .avatar-name {
        font-size: 24px;
        font-weight: bold;
        color: #EB0A1E;
        margin-bottom: 5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    .avatar-title {
        font-size: 14px;
        color: #999;
        margin-bottom: 15px;
    }

    .speak-button {
        background: linear-gradient(135deg, #EB0A1E 0%, #B00000 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(235, 10, 30, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .speak-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(235, 10, 30, 0.6);
    }

    .speak-button:active {
        transform: translateY(0);
    }

    .sound-wave {
        display: inline-flex;
        gap: 3px;
        align-items: center;
        height: 20px;
    }

    .sound-bar {
        width: 3px;
        background: white;
        border-radius: 3px;
        animation: wave 1s ease-in-out infinite;
    }

    .sound-bar:nth-child(1) { height: 8px; animation-delay: 0s; }
    .sound-bar:nth-child(2) { height: 14px; animation-delay: 0.1s; }
    .sound-bar:nth-child(3) { height: 10px; animation-delay: 0.2s; }
    .sound-bar:nth-child(4) { height: 16px; animation-delay: 0.3s; }
    .sound-bar:nth-child(5) { height: 12px; animation-delay: 0.4s; }

    @keyframes wave {
        0%, 100% { height: 8px; }
        50% { height: 20px; }
    }

    .response-bubble {
        background: rgba(235, 10, 30, 0.1);
        border-left: 4px solid #EB0A1E;
        padding: 15px 20px;
        border-radius: 10px;
        margin-top: 15px;
        color: #fff;
        font-size: 14px;
        line-height: 1.6;
        max-width: 600px;
    }
    </style>
    """

def render_avatar(is_speaking=False, show_name=True):
    """Render the Toyota AI avatar"""
    speaking_class = "avatar-speaking" if is_speaking else ""

    avatar_html = f"""
    <div class="avatar-container">
        <div class="avatar-circle {speaking_class}">
            <div class="avatar-icon">🏎️</div>
        </div>
        {f'<div class="avatar-name">GR-Pilot AI</div>' if show_name else ''}
        {f'<div class="avatar-title">Toyota Racing Engineer Assistant</div>' if show_name else ''}
    </div>
    """
    return avatar_html

def render_speak_button(is_speaking=False):
    """Render the speak button with animation"""
    if is_speaking:
        button_html = """
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <button class="speak-button" disabled>
                <div class="sound-wave">
                    <div class="sound-bar"></div>
                    <div class="sound-bar"></div>
                    <div class="sound-bar"></div>
                    <div class="sound-bar"></div>
                    <div class="sound-bar"></div>
                </div>
                <span>Konuşuyor...</span>
            </button>
        </div>
        """
    else:
        button_html = """
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <button class="speak-button">
                <span>🔊</span>
                <span>Sesli Yanıt Al</span>
            </button>
        </div>
        """
    return button_html

def display_ai_response_with_avatar(response_text, enable_audio=False):
    """
    Display AI response with animated avatar

    Args:
        response_text: The AI's text response
        enable_audio: Whether to generate and play audio
    """
    # Inject CSS
    st.markdown(create_toyota_avatar_css(), unsafe_allow_html=True)

    # Create columns for layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Show avatar (speaking if audio enabled)
        st.markdown(render_avatar(is_speaking=enable_audio), unsafe_allow_html=True)

        # Response bubble
        st.markdown(f"""
        <div class="response-bubble">
            {response_text}
        </div>
        """, unsafe_allow_html=True)

        # Audio button
        if st.button("🔊 Sesli Yanıt Al", key="audio_btn", use_container_width=False):
            return True  # Signal to generate audio

    return False

def create_compact_avatar_icon(is_speaking=False):
    """Create a small avatar icon for chat messages"""
    speaking_class = "avatar-speaking" if is_speaking else ""

    return f"""
    <div style="display: inline-block;">
        <div class="avatar-circle {speaking_class}" style="width: 40px; height: 40px; margin: 0;">
            <div class="avatar-icon" style="font-size: 20px;">🏎️</div>
        </div>
    </div>
    """
