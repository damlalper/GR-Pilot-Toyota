import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_telemetry(df, df_ref=None):
    """
    Generates telemetry traces: Speed, RPM, Throttle, Brake.
    Supports comparison with a reference lap (df_ref).
    """
    if df.empty:
        return go.Figure()
    
    # Create subplots
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        subplot_titles=("Speed (km/h)", "RPM", "Throttle & Brake", "Steering Angle"))

    # Main Lap Traces
    fig.add_trace(go.Scatter(x=df['distance'], y=df['speed'], name='Speed (Current)', line=dict(color='cyan')), row=1, col=1)
    if 'nmot' in df.columns:
        fig.add_trace(go.Scatter(x=df['distance'], y=df['nmot'], name='RPM (Current)', line=dict(color='orange')), row=2, col=1)
    if 'ath' in df.columns:
        fig.add_trace(go.Scatter(x=df['distance'], y=df['ath'], name='Throttle (Current)', line=dict(color='green')), row=3, col=1)
    if 'pbrake_f' in df.columns:
        fig.add_trace(go.Scatter(x=df['distance'], y=df['pbrake_f'], name='Brake (Current)', line=dict(color='red')), row=3, col=1)
    if 'Steering_Angle' in df.columns:
        fig.add_trace(go.Scatter(x=df['distance'], y=df['Steering_Angle'], name='Steering (Current)', line=dict(color='magenta')), row=4, col=1)

    # Reference Lap Traces (Ghost)
    if df_ref is not None and not df_ref.empty:
        fig.add_trace(go.Scatter(x=df_ref['distance'], y=df_ref['speed'], name='Speed (Ref)', line=dict(color='rgba(0, 255, 255, 0.3)', dash='dot')), row=1, col=1)
        if 'nmot' in df_ref.columns:
            fig.add_trace(go.Scatter(x=df_ref['distance'], y=df_ref['nmot'], name='RPM (Ref)', line=dict(color='rgba(255, 165, 0, 0.3)', dash='dot')), row=2, col=1)
        if 'ath' in df_ref.columns:
            fig.add_trace(go.Scatter(x=df_ref['distance'], y=df_ref['ath'], name='Throttle (Ref)', line=dict(color='rgba(0, 128, 0, 0.3)', dash='dot')), row=3, col=1)
        if 'pbrake_f' in df_ref.columns:
            fig.add_trace(go.Scatter(x=df_ref['distance'], y=df_ref['pbrake_f'], name='Brake (Ref)', line=dict(color='rgba(255, 0, 0, 0.3)', dash='dot')), row=3, col=1)
        if 'Steering_Angle' in df_ref.columns:
            fig.add_trace(go.Scatter(x=df_ref['distance'], y=df_ref['Steering_Angle'], name='Steering (Ref)', line=dict(color='rgba(255, 0, 255, 0.3)', dash='dot')), row=4, col=1)

    fig.update_layout(
        height=800, 
        template="plotly_dark",
        title_text="Telemetry Analysis (Comparison)",
        xaxis4_title="Distance (m)"
    )
    
    return fig

def plot_track_map(df):
    """
    Generates a 2D track map using WorldPosition coordinates.
    """
    if df.empty:
        return go.Figure()
    
    if 'WorldPositionX' not in df.columns or 'WorldPositionY' not in df.columns:
         return go.Figure().add_annotation(text="No Position Data", showarrow=False)

    fig = px.scatter(
        df, 
        x='WorldPositionX', 
        y='WorldPositionY', 
        color='speed',
        title='Track Map (Speed)',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=600
    )
    return fig
