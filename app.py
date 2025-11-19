import streamlit as st
import pandas as pd
import src.data_loader as dl
import src.visualizations as viz
import src.visualizations_3d as v3d
import src.ai_assistant as ai
import src.analytics as ana
import src.dead_reckoning as dr

# Page Config
st.set_page_config(
    page_title="GR-Pilot: AI Debrief Assistant",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and Header
st.title("🏎️ GR-Pilot: AI Debrief Assistant")
st.markdown("**Toyota GR Cup Series - Post-Race Analytics**")

# Sidebar
with st.sidebar:
    st.header("Settings")
    # File path (hardcoded for now, could be a selector)
    file_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\R2_cota_telemetry_data.csv"
    
    if st.button("Load Data"):
        with st.spinner("Loading data..."):
            st.session_state.df = dl.load_data(file_path)
            
            # Load Auxiliary Data
            lap_times_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\COTA_lap_time_R2.csv"
            st.session_state.lap_times = dl.load_lap_times(lap_times_path)
            
            weather_path = r"c:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2\26_Weather_ Race 2_Anonymized.CSV"
            st.session_state.weather = dl.load_weather(weather_path)
            
        st.success("Data Loaded!")

    # Lap Selection
    if 'df' in st.session_state and not st.session_state.df.empty:
        st.header("Lap Analysis")
        
        # Get unique laps
        laps = sorted(st.session_state.df['lap'].unique())
        
        # Determine Perfect Lap (Fastest)
        best_lap = None
        if 'lap_times' in st.session_state and not st.session_state.lap_times.empty:
            try:
                # Try to find lap_time and lap columns
                # Based on typical TRD data: 'lap_time' (ms) and 'lap_number' or 'lap'
                cols = st.session_state.lap_times.columns
                time_col = next((c for c in cols if 'time' in c.lower() and 'lap' in c.lower()), None)
                lap_col = next((c for c in cols if 'lap' in c.lower() and 'num' in c.lower()), 'lap')
                
                if time_col:
                    # Sort by time
                    best_lap_row = st.session_state.lap_times.sort_values(time_col).iloc[0]
                    best_lap = int(best_lap_row[lap_col]) if lap_col in best_lap_row else None
                    if best_lap:
                        st.sidebar.success(f"Best Lap Detected: {best_lap}")
            except Exception as e:
                st.sidebar.warning(f"Could not auto-detect best lap: {e}")
        
        # Selectors
        selected_lap = st.selectbox("Select Lap to Analyze", laps, index=0)
        
        # Default ref lap to best lap if available
        ref_index = 0
        if best_lap and best_lap in laps:
            # +1 because of None at index 0
            try:
                ref_index = laps.index(best_lap) + 1
            except:
                ref_index = 0
                
        ref_lap = st.selectbox("Select Reference Lap (Ghost)", [None] + laps, index=ref_index)
        
        # Filter Data
        df_lap = st.session_state.df[st.session_state.df['lap'] == selected_lap].copy()
        
        # Reset distance for comparison (start from 0)
        if not df_lap.empty:
            df_lap['distance'] = df_lap['distance'] - df_lap['distance'].iloc[0]
        
        df_ref = None
        if ref_lap is not None:
            df_ref = st.session_state.df[st.session_state.df['lap'] == ref_lap].copy()
            if not df_ref.empty:
                df_ref['distance'] = df_ref['distance'] - df_ref['distance'].iloc[0]

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Telemetry Analysis")
    
    if 'df' in st.session_state and not st.session_state.df.empty:
        # Telemetry Charts
        # Use the filtered df_lap and df_ref
        # We need to ensure these variables are available in this scope
        # Since they are defined in sidebar, we might need to use session state or move logic
        # Streamlit reruns script, so if defined in sidebar, they are available here if sidebar ran first?
        # No, in Streamlit script, variables are global to the run unless inside a function.
        # But `with st.sidebar:` is a context manager. Variables defined inside are available outside? Yes.
        
        # However, if data is not loaded, these vars won't exist.
        # We need to check existence.
        
        if 'df_lap' in locals():
            # Anomaly Detection
            if df_ref is not None and not df_ref.empty:
                anomalies = ana.detect_anomalies(df_lap, df_ref)
                
                if not anomalies.empty:
                    st.warning(f"Detected {len(anomalies)} Performance Anomalies (Speed Delta > 15 km/h)")
                    st.dataframe(anomalies[['distance', 'speed', 'main_speed', 'speed_delta']].head())
                else:
                    st.success("No significant anomalies detected compared to reference.")

            fig_telemetry = viz.plot_telemetry(df_lap, df_ref)
            st.plotly_chart(fig_telemetry, use_container_width=True)
            
            # Track Map Section
            st.subheader("Track Map Analysis")
            
            # Generate Path if missing
            if 'WorldPositionX' not in df_lap.columns:
                df_lap = dr.generate_track_path(df_lap)
            
            map_tabs = st.tabs(["GPS Data (WorldPosition)", "3D Map (Simulation)"])
            
            with map_tabs[0]:
                st.markdown("### 📍 GPS Data (WorldPosition)")
                fig_map = viz.plot_track_map(df_lap)
                st.plotly_chart(fig_map, use_container_width=True)
                
            with map_tabs[1]:
                # Replay Simulation
                st.markdown("### 🏎️ Race Replay")
                progress = st.slider("Replay Lap", 0, len(df_lap)-1, 0, format="")
                
                # Get current car state
                car_state = df_lap.iloc[progress]
                
                # Plot 3D Map with Car Marker
                deck = v3d.plot_3d_track(df_lap, car_index=progress)
                st.pydeck_chart(deck)
                
                # Telemetry at current point
                c1, c2, c3 = st.columns(3)
                c1.metric("Speed", f"{car_state['speed']:.0f} km/h")
                c2.metric("Gear", f"{car_state['gear']:.0f}" if 'gear' in car_state else "N/A")
                c3.metric("RPM", f"{car_state['nmot']:.0f}")
        else:
             st.info("Select a lap to view telemetry.")
            
    else:
        st.info("Please click 'Load Data' in the sidebar.")

# ---------------------------------------------------------
# ADVANCED CHATBOT (Floating UI)
# ---------------------------------------------------------

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS for Floating Button
st.markdown("""
<style>
.floating-chat-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #EB0A1E; /* Toyota Red */
    color: white;
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 24px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    cursor: pointer;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}
.floating-chat-btn:hover {
    background-color: #B00000;
}
</style>
""", unsafe_allow_html=True)

# Chat Interface in Expander (Simulating Floating Window)
with st.sidebar.expander("💬 GR-Pilot Assistant", expanded=True):
    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "plot" in msg and msg["plot"] is not None:
                st.plotly_chart(msg["plot"], use_container_width=True)
    
    # Input
    if prompt := st.chat_input("Ask about your lap..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate Response
        with st.spinner("Analyzing..."):
            # Context
            df_context = st.session_state.df if 'df' in st.session_state else None
            df_ref_context = st.session_state.df[st.session_state.df['lap'] == ref_lap] if 'df' in st.session_state and ref_lap else None
            weather_context = st.session_state.weather if 'weather' in st.session_state else None
            
            ai_response = ai.query_ai(df_context, prompt, df_ref=df_ref_context, weather_df=weather_context)
            
            # Handle Dict Response
            if isinstance(ai_response, dict):
                response_text = ai_response["text"]
                response_plot = ai_response["plot"]
            else:
                response_text = ai_response
                response_plot = None
            
            # Audio Generation (TTS)
            audio_file = ai.generate_audio(response_text)
        
        # Add AI message
        # We need to store the plot in history too if we want it to persist, 
        # but Streamlit session state might get heavy. 
        # For now, let's just store text and maybe a flag or the plot object (if serializable).
        # Plotly figures are JSON serializable-ish.
        st.session_state.messages.append({"role": "assistant", "content": response_text, "plot": response_plot})
        
        with st.chat_message("assistant"):
            st.markdown(response_text)
            if response_plot:
                st.plotly_chart(response_plot, use_container_width=True)
            if audio_file:
                st.audio(audio_file, format='audio/mp3')
