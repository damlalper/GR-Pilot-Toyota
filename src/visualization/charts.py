"""
Advanced Plotly Chart Components
Toyota GR branded, interactive visualizations
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple

# Toyota GR Colors
TOYOTA_RED = '#FF0000'
TOYOTA_DARK_BG = '#0E1117'
TOYOTA_SECONDARY_BG = '#262730'
TOYOTA_TEXT_WHITE = '#FAFAFA'
TOYOTA_TEXT_GRAY = '#A0A0A0'
TOYOTA_SUCCESS = '#00D26A'
TOYOTA_WARNING = '#FFD600'
TOYOTA_ERROR = '#FF4B4B'


def get_plotly_theme() -> dict:
    """
    Toyota GR themed Plotly layout template
    """
    return {
        'plot_bgcolor': TOYOTA_SECONDARY_BG,
        'paper_bgcolor': TOYOTA_DARK_BG,
        'font': {'color': TOYOTA_TEXT_WHITE, 'family': 'Helvetica Neue, Arial'},
        'xaxis': {
            'gridcolor': '#3a3a3a',
            'zerolinecolor': '#3a3a3a',
            'color': TOYOTA_TEXT_WHITE
        },
        'yaxis': {
            'gridcolor': '#3a3a3a',
            'zerolinecolor': '#3a3a3a',
            'color': TOYOTA_TEXT_WHITE
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': TOYOTA_SECONDARY_BG,
            'font_size': 12,
            'font_family': 'Helvetica Neue'
        }
    }


def create_lap_time_evolution(df: pd.DataFrame, lap_col: str = 'LapNumber') -> go.Figure:
    """
    Lap time evolution chart with best lap highlight

    Args:
        df: DataFrame with lap times
        lap_col: Column name for lap number

    Returns:
        Plotly Figure
    """
    if lap_col not in df.columns:
        return go.Figure()

    # Calculate lap times (assuming we have timestamp data)
    if 'TimeStamp' in df.columns and 'LapTime' not in df.columns:
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
        lap_times = df.groupby(lap_col)['TimeStamp'].agg(['min', 'max'])
        lap_times['LapTime'] = (lap_times['max'] - lap_times['min']).dt.total_seconds()
    elif 'LapTime' in df.columns:
        lap_times = df.groupby(lap_col)['LapTime'].mean().reset_index()
    else:
        # Fallback: calculate from speed
        if 'Speed' in df.columns:
            lap_times = df.groupby(lap_col).agg({
                'Speed': 'mean'
            }).reset_index()
            # Estimate lap time (inverse of speed)
            lap_times['LapTime'] = 1000 / lap_times['Speed']
        else:
            return go.Figure()

    lap_times = lap_times.reset_index() if isinstance(lap_times, pd.DataFrame) and 'LapTime' in lap_times.columns else lap_times

    # Find best lap
    if 'LapTime' in lap_times.columns:
        best_lap_idx = lap_times['LapTime'].idxmin()
        best_lap_num = lap_times.loc[best_lap_idx, lap_col] if lap_col in lap_times.columns else best_lap_idx
        best_lap_time = lap_times.loc[best_lap_idx, 'LapTime']
    else:
        best_lap_num = 0
        best_lap_time = 0

    fig = go.Figure()

    # Main line
    fig.add_trace(go.Scatter(
        x=lap_times[lap_col] if lap_col in lap_times.columns else lap_times.index,
        y=lap_times['LapTime'] if 'LapTime' in lap_times.columns else lap_times.values,
        mode='lines+markers',
        name='Lap Time',
        line=dict(color=TOYOTA_RED, width=3),
        marker=dict(size=8, color=TOYOTA_RED),
        hovertemplate='<b>Lap %{x}</b><br>Time: %{y:.3f}s<extra></extra>'
    ))

    # Best lap marker
    if 'LapTime' in lap_times.columns:
        fig.add_trace(go.Scatter(
            x=[best_lap_num],
            y=[best_lap_time],
            mode='markers',
            name='Best Lap',
            marker=dict(
                size=16,
                color=TOYOTA_SUCCESS,
                symbol='star',
                line=dict(color=TOYOTA_TEXT_WHITE, width=2)
            ),
            hovertemplate=f'<b>Best Lap {best_lap_num}</b><br>Time: {best_lap_time:.3f}s<extra></extra>'
        ))

    # Average line
    if 'LapTime' in lap_times.columns:
        avg_time = lap_times['LapTime'].mean()
        fig.add_hline(
            y=avg_time,
            line_dash='dash',
            line_color=TOYOTA_TEXT_GRAY,
            annotation_text=f'Avg: {avg_time:.3f}s',
            annotation_position='right'
        )

    fig.update_layout(
        title={
            'text': '🏁 Lap Time Evolution',
            'font': {'size': 20, 'color': TOYOTA_TEXT_WHITE}
        },
        xaxis_title='Lap Number',
        yaxis_title='Lap Time (seconds)',
        **get_plotly_theme(),
        showlegend=True,
        legend=dict(
            bgcolor=TOYOTA_SECONDARY_BG,
            bordercolor=TOYOTA_RED,
            borderwidth=1
        ),
        height=400
    )

    return fig


def create_speed_trace(df: pd.DataFrame, lap_num: Optional[int] = None) -> go.Figure:
    """
    Speed trace visualization with distance/time

    Args:
        df: DataFrame with Speed column
        lap_num: Specific lap to show (None = all data)

    Returns:
        Plotly Figure
    """
    if 'Speed' not in df.columns:
        return go.Figure()

    # Filter by lap if specified
    if lap_num is not None and 'LapNumber' in df.columns:
        data = df[df['LapNumber'] == lap_num].copy()
        title = f'Speed Trace - Lap {lap_num}'
    else:
        data = df.copy()
        title = 'Speed Trace - All Laps'

    # Create distance axis if not exists
    if 'Distance' not in data.columns and 'TimeStamp' in data.columns:
        data['TimeStamp'] = pd.to_datetime(data['TimeStamp'])
        data['Time'] = (data['TimeStamp'] - data['TimeStamp'].iloc[0]).dt.total_seconds()
        x_data = data['Time']
        x_title = 'Time (seconds)'
    elif 'Distance' in data.columns:
        x_data = data['Distance']
        x_title = 'Distance (m)'
    else:
        x_data = data.index
        x_title = 'Data Point'

    fig = go.Figure()

    # Speed trace
    fig.add_trace(go.Scatter(
        x=x_data,
        y=data['Speed'],
        mode='lines',
        name='Speed',
        line=dict(color=TOYOTA_RED, width=2),
        fill='tozeroy',
        fillcolor=f'rgba(255, 0, 0, 0.2)',
        hovertemplate='<b>Speed: %{y:.1f} km/h</b><br>Position: %{x:.1f}<extra></extra>'
    ))

    # Add max speed marker
    max_speed_idx = data['Speed'].idxmax()
    max_speed = data.loc[max_speed_idx, 'Speed']
    max_speed_x = x_data.iloc[data.index.get_loc(max_speed_idx)] if hasattr(x_data, 'iloc') else x_data[max_speed_idx]

    fig.add_trace(go.Scatter(
        x=[max_speed_x],
        y=[max_speed],
        mode='markers+text',
        name='Max Speed',
        marker=dict(size=12, color=TOYOTA_SUCCESS, symbol='triangle-up'),
        text=[f'{max_speed:.1f} km/h'],
        textposition='top center',
        textfont=dict(color=TOYOTA_SUCCESS, size=10),
        hovertemplate=f'<b>Max Speed</b><br>{max_speed:.1f} km/h<extra></extra>'
    ))

    fig.update_layout(
        title={'text': f'🏎️ {title}', 'font': {'size': 20}},
        xaxis_title=x_title,
        yaxis_title='Speed (km/h)',
        **get_plotly_theme(),
        height=400
    )

    return fig


def create_telemetry_overlay(
    df: pd.DataFrame,
    channels: List[str] = ['Speed', 'BrakePressure', 'Throttle'],
    lap_num: Optional[int] = None
) -> go.Figure:
    """
    Multi-channel telemetry overlay

    Args:
        df: DataFrame
        channels: List of columns to plot
        lap_num: Specific lap

    Returns:
        Plotly Figure with subplots
    """
    # Filter data
    if lap_num is not None and 'LapNumber' in df.columns:
        data = df[df['LapNumber'] == lap_num].copy()
    else:
        data = df.copy()

    # Filter available channels
    available_channels = [ch for ch in channels if ch in data.columns]

    if not available_channels:
        return go.Figure()

    # Create subplots
    fig = make_subplots(
        rows=len(available_channels),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[f'<b>{ch}</b>' for ch in available_channels]
    )

    # X-axis
    if 'TimeStamp' in data.columns:
        data['TimeStamp'] = pd.to_datetime(data['TimeStamp'])
        x_data = (data['TimeStamp'] - data['TimeStamp'].iloc[0]).dt.total_seconds()
        x_title = 'Time (s)'
    else:
        x_data = data.index
        x_title = 'Data Point'

    # Add traces
    colors = [TOYOTA_RED, '#FF6600', '#FFAA00', '#00D26A', '#0066CC']

    for i, channel in enumerate(available_channels):
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=data[channel],
                mode='lines',
                name=channel,
                line=dict(color=colors[i % len(colors)], width=2),
                showlegend=False
            ),
            row=i+1,
            col=1
        )

        # Update y-axis title
        fig.update_yaxes(
            title_text=channel,
            row=i+1,
            col=1,
            gridcolor='#3a3a3a'
        )

    # Update x-axis
    fig.update_xaxes(
        title_text=x_title,
        row=len(available_channels),
        col=1,
        gridcolor='#3a3a3a'
    )

    fig.update_layout(
        title={
            'text': f'📊 Telemetry Overlay - Lap {lap_num if lap_num else "All"}',
            'font': {'size': 20}
        },
        plot_bgcolor=TOYOTA_SECONDARY_BG,
        paper_bgcolor=TOYOTA_DARK_BG,
        font={'color': TOYOTA_TEXT_WHITE},
        height=150 * len(available_channels),
        hovermode='x unified'
    )

    return fig


def create_cpi_breakdown_chart(cpi_result: Dict) -> go.Figure:
    """
    CPI breakdown radar/bar chart

    Args:
        cpi_result: CPI calculation result dict

    Returns:
        Plotly Figure
    """
    if 'breakdown' not in cpi_result:
        return go.Figure()

    breakdown = cpi_result['breakdown']

    categories = list(breakdown.keys())
    values = list(breakdown.values())

    # Create radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=f'rgba(255, 0, 0, 0.3)',
        line=dict(color=TOYOTA_RED, width=3),
        marker=dict(size=8, color=TOYOTA_RED),
        name='Performance'
    ))

    # Add reference circle at 80
    fig.add_trace(go.Scatterpolar(
        r=[80] * len(categories),
        theta=categories,
        mode='lines',
        line=dict(color=TOYOTA_TEXT_GRAY, dash='dash', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color=TOYOTA_TEXT_WHITE),
                gridcolor='#3a3a3a'
            ),
            angularaxis=dict(
                tickfont=dict(color=TOYOTA_TEXT_WHITE, size=11)
            ),
            bgcolor=TOYOTA_SECONDARY_BG
        ),
        title={
            'text': f'📈 CPI Breakdown - Score: {cpi_result["total_cpi"]}/100',
            'font': {'size': 20, 'color': TOYOTA_TEXT_WHITE}
        },
        paper_bgcolor=TOYOTA_DARK_BG,
        font={'color': TOYOTA_TEXT_WHITE},
        height=500,
        showlegend=False
    )

    return fig


def create_cpi_trend(lap_cpis: Dict[int, Dict]) -> go.Figure:
    """
    CPI trend across laps

    Args:
        lap_cpis: Dict of {lap_num: cpi_result}

    Returns:
        Plotly Figure
    """
    if not lap_cpis:
        return go.Figure()

    laps = sorted(lap_cpis.keys())
    cpi_scores = [lap_cpis[lap]['total_cpi'] for lap in laps]
    grades = [lap_cpis[lap]['grade'] for lap in laps]

    fig = go.Figure()

    # CPI line
    fig.add_trace(go.Scatter(
        x=laps,
        y=cpi_scores,
        mode='lines+markers',
        name='CPI Score',
        line=dict(color=TOYOTA_RED, width=3),
        marker=dict(
            size=10,
            color=cpi_scores,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title='CPI', tickfont=dict(color=TOYOTA_TEXT_WHITE))
        ),
        text=[f'Grade: {g}' for g in grades],
        hovertemplate='<b>Lap %{x}</b><br>CPI: %{y:.1f}/100<br>%{text}<extra></extra>'
    ))

    # Average line
    avg_cpi = np.mean(cpi_scores)
    fig.add_hline(
        y=avg_cpi,
        line_dash='dash',
        line_color=TOYOTA_TEXT_GRAY,
        annotation_text=f'Average: {avg_cpi:.1f}',
        annotation_position='right'
    )

    # Grade thresholds
    thresholds = [(90, 'A'), (80, 'B'), (70, 'C'), (60, 'D')]
    for threshold, grade in thresholds:
        fig.add_hline(
            y=threshold,
            line_dash='dot',
            line_color='#444',
            line_width=1,
            annotation_text=grade,
            annotation_position='left',
            annotation_font_size=10
        )

    fig.update_layout(
        title={'text': '📊 CPI Evolution', 'font': {'size': 20}},
        xaxis_title='Lap Number',
        yaxis_title='CPI Score',
        **get_plotly_theme(),
        yaxis=dict(range=[0, 100]),
        height=400
    )

    return fig


def create_sector_heatmap(sector_data: Dict[int, Dict]) -> go.Figure:
    """
    Sector performance heatmap

    Args:
        sector_data: {sector_num: {metrics}}

    Returns:
        Plotly Figure
    """
    if not sector_data:
        return go.Figure()

    sectors = sorted(sector_data.keys())

    # Extract metrics
    avg_times = [sector_data[s].get('avg_time', 0) for s in sectors]
    best_times = [sector_data[s].get('best_time', 0) for s in sectors]
    deltas = [sector_data[s].get('delta_to_best', 0) for s in sectors]

    fig = go.Figure()

    # Delta bars (time loss)
    fig.add_trace(go.Bar(
        x=[f'S{s}' for s in sectors],
        y=deltas,
        marker=dict(
            color=deltas,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title='Time Loss (s)', tickfont=dict(color=TOYOTA_TEXT_WHITE))
        ),
        text=[f'+{d:.3f}s' if d > 0 else f'{d:.3f}s' for d in deltas],
        textposition='outside',
        textfont=dict(color=TOYOTA_TEXT_WHITE),
        hovertemplate='<b>Sector %{x}</b><br>Time Loss: %{y:.3f}s<extra></extra>'
    ))

    fig.update_layout(
        title={'text': '🗺️ Sector Time Loss Heatmap', 'font': {'size': 20}},
        xaxis_title='Sector',
        yaxis_title='Time Loss vs Best (seconds)',
        **get_plotly_theme(),
        height=400
    )

    return fig


def create_anomaly_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Anomaly detection timeline

    Args:
        df: DataFrame with anomaly flags

    Returns:
        Plotly Figure
    """
    if 'total_anomalies' not in df.columns:
        return go.Figure()

    # X-axis
    if 'TimeStamp' in df.columns:
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
        x_data = (df['TimeStamp'] - df['TimeStamp'].iloc[0]).dt.total_seconds()
        x_title = 'Time (s)'
    else:
        x_data = df.index
        x_title = 'Data Point'

    fig = go.Figure()

    # Anomaly scatter
    anomalies = df[df['total_anomalies'] > 0]

    if len(anomalies) > 0:
        anomaly_x = x_data[anomalies.index] if hasattr(x_data, 'iloc') else x_data.iloc[anomalies.index]

        fig.add_trace(go.Scatter(
            x=anomaly_x,
            y=anomalies['total_anomalies'],
            mode='markers',
            name='Anomalies',
            marker=dict(
                size=anomalies['total_anomalies'] * 5 + 5,
                color=TOYOTA_ERROR,
                symbol='x',
                line=dict(width=2, color=TOYOTA_TEXT_WHITE)
            ),
            hovertemplate='<b>Anomaly Detected</b><br>Count: %{y}<br>Position: %{x:.1f}<extra></extra>'
        ))

    fig.update_layout(
        title={'text': '⚠️ Anomaly Detection Timeline', 'font': {'size': 20}},
        xaxis_title=x_title,
        yaxis_title='Anomaly Count',
        **get_plotly_theme(),
        height=300
    )

    return fig


def create_performance_gauge(cpi_score: float) -> go.Figure:
    """
    CPI gauge chart

    Args:
        cpi_score: CPI value (0-100)

    Returns:
        Plotly Figure
    """
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=cpi_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Composite Performance Index', 'font': {'size': 20, 'color': TOYOTA_TEXT_WHITE}},
        delta={'reference': 80, 'increasing': {'color': TOYOTA_SUCCESS}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': TOYOTA_TEXT_WHITE},
            'bar': {'color': TOYOTA_RED, 'thickness': 0.8},
            'bgcolor': TOYOTA_SECONDARY_BG,
            'borderwidth': 2,
            'bordercolor': TOYOTA_TEXT_GRAY,
            'steps': [
                {'range': [0, 60], 'color': '#444'},
                {'range': [60, 70], 'color': '#555'},
                {'range': [70, 80], 'color': '#666'},
                {'range': [80, 90], 'color': '#777'},
                {'range': [90, 100], 'color': '#888'}
            ],
            'threshold': {
                'line': {'color': TOYOTA_SUCCESS, 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor=TOYOTA_DARK_BG,
        font={'color': TOYOTA_TEXT_WHITE, 'family': 'Helvetica Neue'},
        height=350
    )

    return fig
