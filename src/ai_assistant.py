from gtts import gTTS
import tempfile

def generate_audio(text):
    """
    Generates an audio file from text using gTTS.
    Returns the path to the temporary file.
    """
    try:
        tts = gTTS(text=text, lang='en')
        # Create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

import plotly.express as px

def query_ai(df, question, df_ref=None, weather_df=None):
    """
    Mock function to simulate AI response.
    Returns a dictionary: {"text": str, "plot": plotly.Figure (optional)}
    """
    response = {"text": "", "plot": None}
    
    if df is None or df.empty:
        response["text"] = "I need data to answer that. Please load the telemetry first."
        return response
    
    question = question.lower()
    
    # Weather Context
    weather_info = ""
    if weather_df is not None and not weather_df.empty:
        if 'TRACK_TEMP' in weather_df.columns:
            avg_temp = weather_df['TRACK_TEMP'].mean()
            weather_info = f" (Track Temp: {avg_temp:.1f}C)"
    
    # Comparison Logic
    if df_ref is not None and not df_ref.empty and ("compare" in question or "difference" in question or "faster" in question or "slower" in question):
        avg_speed_main = df['speed'].mean()
        avg_speed_ref = df_ref['speed'].mean()
        diff = avg_speed_main - avg_speed_ref
        status = "faster" if diff > 0 else "slower"
        response["text"] = f"Comparing the laps{weather_info}: Your selected lap average speed was {avg_speed_main:.2f} km/h, while the reference lap was {avg_speed_ref:.2f} km/h. You were {abs(diff):.2f} km/h {status} on average."
        
        # Visual: Speed Comparison
        fig = px.line(df, x='distance', y='speed', title='Speed Comparison')
        fig.add_scatter(x=df_ref['distance'], y=df_ref['speed'], mode='lines', name='Reference', line=dict(dash='dot', color='white'))
        response["plot"] = fig
        return response

    # Single Lap Logic
    if "speed" in question:
        max_speed = df['speed'].max()
        avg_speed = df['speed'].mean()
        response["text"] = f"Based on this lap, the maximum speed reached was {max_speed:.2f} km/h, with an average of {avg_speed:.2f} km/h."
        # Visual: Speed Histogram
        response["plot"] = px.histogram(df, x="speed", title="Speed Distribution", nbins=50)
        return response
    
    if "rpm" in question or "engine" in question:
        max_rpm = df['nmot'].max()
        response["text"] = f"The engine pushed to a maximum of {max_rpm:.0f} RPM."
        response["plot"] = px.line(df, x='distance', y='nmot', title='RPM Trace')
        return response
        
    if "brake" in question:
        response["text"] = "Braking analysis requires more specific event detection, but I can see several heavy braking zones in the telemetry."
        if 'pbrake_f' in df.columns:
             response["plot"] = px.line(df, x='distance', y='pbrake_f', title='Brake Pressure (Front)')
        return response
        
    if "steering" in question or "angle" in question:
        if 'Steering_Angle' in df.columns:
            max_steer = df['Steering_Angle'].abs().max()
            response["text"] = f"Your maximum steering angle was {max_steer:.1f} degrees. Here is the distribution of your steering inputs."
            response["plot"] = px.histogram(df, x="Steering_Angle", title="Steering Angle Distribution", nbins=50)
        else:
            response["text"] = "Steering data is not available."
        return response

    if "throttle" in question or "gas" in question:
        if 'ath' in df.columns:
            avg_throttle = df['ath'].mean()
            response["text"] = f"Your average throttle application was {avg_throttle:.1f}%."
            response["plot"] = px.line(df, x='distance', y='ath', title='Throttle Position')
        else:
             response["text"] = "Throttle data is not available."
        return response

    if "distance" in question:
        total_dist = df['distance'].max()
        response["text"] = f"The total distance covered in this lap segment is {total_dist:.2f} meters."
        return response

    response["text"] = "That's an interesting question. In the full version, I would analyze the specific lap segments to answer that. For now, I can tell you about Speed, RPM, Brake, Throttle, and Steering."
    return response
