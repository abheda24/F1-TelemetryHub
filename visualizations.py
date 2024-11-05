import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
import seaborn as sns
import matplotlib.pyplot as plt
import fastf1
import fastf1.core
from pathlib import Path
import logging
from data_processor import SessionData 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class F1Visualizations:
    """ F1 data visualization class."""

    # Color schemes
    F1_COLORS = {
        'background': '#15151e',
        'primary': '#e10600',
        'secondary': '#ffffff',
        'grid': '#38383f',
        'text': '#ffffff',
        'accent': '#ff0090',
    }

    TEAM_COLORS = {
        'Red Bull Racing': '#3671C6',
        'Mercedes': '#6CD3BF',
        'Ferrari': '#F91536',
        'McLaren': '#F58020',
        'Aston Martin': '#358C75',
        'Alpine': '#2293D1',
        'Williams': '#37BEDD',
        'AlphaTauri': '#6692FF',
        'Alfa Romeo': '#C92D4B',
        'Haas F1 Team': '#B6BABD',
    }

    TYRE_COLORS = {
        'SOFT': '#FF0000',
        'MEDIUM': '#FFF200',
        'HARD': '#FFFFFF',
        'INTERMEDIATE': '#43B02A',
        'WET': '#0067FF'
    }

    def __init__(self):
        """Initialize visualization settings."""
        # Setup matplotlib for F1
        fastf1.plotting.setup_mpl(
            mpl_timedelta_support=True,
            misc_mpl_mods=False,
            color_scheme='fastf1'
        )
        
        # Base Plotly layout
        self.base_layout = {
            'paper_bgcolor': self.F1_COLORS['background'],
            'plot_bgcolor': self.F1_COLORS['background'],
            'font': {
                'family': "Titillium Web, sans-serif",
                'color': self.F1_COLORS['text']
            },
            'xaxis': {
                'gridcolor': self.F1_COLORS['grid'],
                'showline': True,
                'linecolor': self.F1_COLORS['grid'],
                'zeroline': False
            },
            'yaxis': {
                'gridcolor': self.F1_COLORS['grid'],
                'showline': True,
                'linecolor': self.F1_COLORS['grid'],
                'zeroline': False
            },
            'margin': {'t': 50, 'l': 50, 'r': 50, 'b': 50},
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(0,0,0,0.5)',
                'bordercolor': self.F1_COLORS['grid']
            }
        }

    def create_lap_time_chart(self, timing_data: pd.DataFrame) -> go.Figure:
        """Create interactive lap time comparison chart."""
        try:
            fig = go.Figure()

            for driver in timing_data['Driver'].unique():
                driver_data = timing_data[timing_data['Driver'] == driver]
                team = driver_data['Team'].iloc[0] if 'Team' in driver_data.columns else 'Unknown'
                color = self.TEAM_COLORS.get(team, self.F1_COLORS['secondary'])

                # Convert lap times to seconds if needed
                if 'LapTimeSeconds' not in driver_data.columns:
                    driver_data['LapTimeSeconds'] = driver_data['LapTime'].dt.total_seconds()

                fig.add_trace(go.Scatter(
                    x=driver_data['LapNumber'],
                    y=driver_data['LapTimeSeconds'],
                    name=driver,
                    line=dict(color=color, width=2),
                    mode='lines+markers',
                    marker=dict(size=6),
                    hovertemplate=(
                        f"Driver: {driver}<br>" +
                        "Lap: %{x}<br>" +
                        "Time: %{y:.3f}s<br>" +
                        "<extra></extra>"
                    )
                ))

            layout = self.base_layout.copy()
            layout.update({
                'title': "Lap Time Comparison",
                'xaxis_title': "Lap Number",
                'yaxis_title': "Lap Time (seconds)",
                'hovermode': 'x unified'
            })
            fig.update_layout(layout)

            return fig
        except Exception as e:
            logger.error(f"Error creating lap time chart: {e}")
            return go.Figure()

    def create_position_changes_chart(self, timing_data: pd.DataFrame) -> go.Figure:
        """Create interactive position changes visualization."""
        try:
            fig = go.Figure()
            
            # Make sure we have the required columns
            if not all(col in timing_data.columns for col in ['Driver', 'LapNumber', 'Position']):
                logger.error("Missing required columns in timing data")
                return go.Figure()

            # Process each driver's data
            for driver in timing_data['Driver'].unique():
                driver_data = timing_data[timing_data['Driver'] == driver].copy()
                
                # Sort by lap number to ensure correct line plotting
                driver_data = driver_data.sort_values('LapNumber')
                
                # Get team color
                team = driver_data['Team'].iloc[0] if 'Team' in driver_data.columns else 'Unknown'
                color = self.TEAM_COLORS.get(team, self.F1_COLORS['secondary'])
                
                # Add trace for this driver
                fig.add_trace(go.Scatter(
                    x=driver_data['LapNumber'],
                    y=driver_data['Position'],
                    name=driver,
                    line=dict(
                        color=color,
                        width=2,
                    ),
                    mode='lines+markers',
                    marker=dict(size=6),
                    hovertemplate=(
                        f"Driver: {driver}<br>" +
                        "Lap: %{x}<br>" +
                        "Position: %{y}<br>" +
                        "<extra></extra>"
                    )
                ))

            # Update layout with F1-style configuration
            layout = self.base_layout.copy()
            layout.update({
                'title': "Position Changes",
                'xaxis_title': "Lap Number",
                'yaxis_title': "Position",
                'xaxis': {
                    'gridcolor': self.F1_COLORS['grid'],
                    'showline': True,
                    'linecolor': self.F1_COLORS['grid'],
                    'tickmode': 'linear',
                    'dtick': 5  # Show every 5th lap
                },
                'yaxis': {
                    'gridcolor': self.F1_COLORS['grid'],
                    'showline': True,
                    'linecolor': self.F1_COLORS['grid'],
                    'autorange': 'reversed',  # Invert Y-axis
                    'tickmode': 'array',
                    'tickvals': [1, 5, 10, 15, 20],  # Standard F1 position ticks
                    'range': [20.5, 0.5]  # Ensure proper range with padding
                },
                'hovermode': 'closest',
                'showlegend': True,
                'legend': {
                    'bgcolor': 'rgba(0,0,0,0.5)',
                    'bordercolor': self.F1_COLORS['grid'],
                    'x': 1.1,  # Place legend outside the plot
                    'y': 1
                }
            })
            fig.update_layout(layout)

            return fig
            
        except Exception as e:
            logger.error(f"Error creating position changes chart: {e}")
            return go.Figure()

    def create_speed_trace(self, telemetry_data: pd.DataFrame, driver: str, team: str) -> go.Figure:
        """Create interactive speed trace visualization."""
        try:
            fig = go.Figure()
            color = self.TEAM_COLORS.get(team, self.F1_COLORS['secondary'])

            fig.add_trace(go.Scatter(
                x=telemetry_data['Distance'],
                y=telemetry_data['Speed'],
                name=f'{driver} Speed',
                line=dict(color=color, width=2),
                mode='lines',
                hovertemplate=(
                    f"Driver: {driver}<br>" +
                    "Distance: %{x:.0f}m<br>" +
                    "Speed: %{y:.1f}km/h<br>" +
                    "<extra></extra>"
                )
            ))

            layout = self.base_layout.copy()
            layout.update({
                'title': f"Speed Trace - {driver}",
                'xaxis_title': "Distance (m)",
                'yaxis_title': "Speed (km/h)"
            })
            fig.update_layout(layout)

            return fig
        except Exception as e:
            logger.error(f"Error creating speed trace: {e}")
            return go.Figure()

    def create_gear_shifts(self, telemetry_data: pd.DataFrame, driver: str, team: str) -> go.Figure:
        """Create interactive gear shifts visualization."""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=("Speed", "Gear")
            )

            color = self.TEAM_COLORS.get(team, self.F1_COLORS['secondary'])

            # Speed trace
            fig.add_trace(
                go.Scatter(
                    x=telemetry_data['Distance'],
                    y=telemetry_data['Speed'],
                    name='Speed',
                    line=dict(color=color, width=2),
                    mode='lines',
                    hovertemplate="Speed: %{y:.1f}km/h<br>Distance: %{x:.0f}m<extra></extra>"
                ),
                row=1, col=1
            )

            # Gear trace
            fig.add_trace(
                go.Scatter(
                    x=telemetry_data['Distance'],
                    y=telemetry_data['nGear'],
                    name='Gear',
                    line=dict(color=self.F1_COLORS['accent'], width=2),
                    mode='lines',
                    hovertemplate="Gear: %{y}<br>Distance: %{x:.0f}m<extra></extra>"
                ),
                row=2, col=1
            )

            layout = self.base_layout.copy()
            layout.update({
                'title': f"Gear Shifts - {driver}",
                'height': 600,
                'showlegend': True,
                'legend': dict(x=1.1, y=1)
            })
            fig.update_layout(layout)

            # Update axes labels
            fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
            fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
            fig.update_yaxes(title_text="Gear", row=2, col=1)

            return fig
        except Exception as e:
            logger.error(f"Error creating gear shifts visualization: {e}")
            return go.Figure()

    def create_tyre_strategy(self, timing_data: pd.DataFrame) -> go.Figure:
        """Create interactive tyre strategy visualization."""
        try:
            fig = go.Figure()

            for driver in timing_data['Driver'].unique():
                driver_data = timing_data[timing_data['Driver'] == driver]
                
                for compound in driver_data['Compound'].unique():
                    compound_data = driver_data[driver_data['Compound'] == compound]
                    color = self.TYRE_COLORS.get(compound.upper(), '#FFFFFF')

                    fig.add_trace(go.Scatter(
                        x=compound_data['LapNumber'],
                        y=[driver] * len(compound_data),
                        name=f"{driver} - {compound}",
                        mode='markers',
                        marker=dict(color=color, size=12),
                        showlegend=(driver == timing_data['Driver'].unique()[0]),
                        hovertemplate=(
                            f"Driver: {driver}<br>" +
                            "Lap: %{x}<br>" +
                            f"Compound: {compound}<br>" +
                            "<extra></extra>"
                        )
                    ))

            layout = self.base_layout.copy()
            layout.update({
                'title': "Tyre Strategy",
                'xaxis_title': "Lap Number",
                'yaxis_title': "Driver",
                'height': 600
            })
            fig.update_layout(layout)

            return fig
        except Exception as e:
            logger.error(f"Error creating tyre strategy visualization: {e}")
            return go.Figure()

    def create_driver_comparison(
        self,
        telemetry_data1: pd.DataFrame,
        telemetry_data2: pd.DataFrame,
        driver1: str,
        driver2: str,
        team1: str,
        team2: str
    ) -> go.Figure:
        """Create interactive driver comparison visualization."""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=("Speed Comparison", "Speed Delta")
            )

            color1 = self.TEAM_COLORS.get(team1, self.F1_COLORS['secondary'])
            color2 = self.TEAM_COLORS.get(team2, self.F1_COLORS['secondary'])

            # Speed comparison
            fig.add_trace(
                go.Scatter(
                    x=telemetry_data1['Distance'],
                    y=telemetry_data1['Speed'],
                    name=f'{driver1} Speed',
                    line=dict(color=color1, width=2),
                    mode='lines'
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=telemetry_data2['Distance'],
                    y=telemetry_data2['Speed'],
                    name=f'{driver2} Speed',
                    line=dict(color=color2, width=2),
                    mode='lines'
                ),
                row=1, col=1
            )

            # Calculate and plot speed delta
            merged_data = pd.merge_asof(
                telemetry_data1[['Distance', 'Speed']].sort_values('Distance'),
                telemetry_data2[['Distance', 'Speed']].sort_values('Distance'),
                on='Distance',
                suffixes=('_1', '_2')
            )
            
            speed_delta = merged_data['Speed_1'] - merged_data['Speed_2']

            fig.add_trace(
                go.Scatter(
                    x=merged_data['Distance'],
                    y=speed_delta,
                    name='Speed Delta',
                    fill='tozeroy',
                    line=dict(color=self.F1_COLORS['accent']),
                    mode='lines'
                ),
                row=2, col=1
            )

            layout = self.base_layout.copy()
            layout.update({
                'title': f"{driver1} vs {driver2} Comparison",
                'height': 800
            })
            fig.update_layout(layout)

            # Update axes labels
            fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
            fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
            fig.update_yaxes(title_text="Speed Delta (km/h)", row=2, col=1)

            return fig
        except Exception as e:
            logger.error(f"Error creating driver comparison: {e}")
            return go.Figure()

    
    def create_weather_chart(self, weather_data: pd.DataFrame) -> go.Figure:
        """Create interactive weather conditions visualization."""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=("Temperature", "Other Conditions")
            )

            # Temperature traces
            fig.add_trace(
                go.Scatter(
                    x=weather_data['Time'].dt.total_seconds(),
                    y=weather_data['TrackTemp'],
                    name='Track Temperature',
                    line=dict(color='#FF5733', width=2),
                    mode='lines'
                ),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=weather_data['Time'].dt.total_seconds(),
                    y=weather_data['AirTemp'],
                    name='Air Temperature',
                    line=dict(color='#33C1FF', width=2),
                    mode='lines'
                ),
                row=1, col=1
            )

            # Humidity and wind speed
            fig.add_trace(
                go.Scatter(
                    x=weather_data['Time'].dt.total_seconds(),
                    y=weather_data['Humidity'],
                    name='Humidity',
                    line=dict(color='#33FF57', width=2),
                    mode='lines'
                ),
                row=2, col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=weather_data['Time'].dt.total_seconds(),
                    y=weather_data['WindSpeed'],
                    name='Wind Speed',
                    line=dict(color='#FF33FF', width=2),
                    mode='lines'
                ),
                row=2, col=1
            )

            # Update layout
            layout = self.base_layout.copy()
            layout.update({
                'title': "Weather Conditions",
                'height': 700,
                'showlegend': True,
                'legend': dict(x=1.1, y=1),
                'xaxis2': {
                    'title': "Time (HH:MM:SS)",
                    'tickmode': 'array',
                    'ticktext': [format_timedelta(pd.Timedelta(seconds=x)) 
                                for x in weather_data['Time'].dt.total_seconds()],
                    'tickvals': weather_data['Time'].dt.total_seconds()
                }
            })
            fig.update_layout(layout)

            # Update axes labels
            fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
            fig.update_yaxes(title_text="Value", row=2, col=1)

            return fig
        except Exception as e:
            logger.error(f"Error creating weather chart: {e}")
            return go.Figure()

def format_timedelta(td: pd.Timedelta) -> str:
    """Format timedelta to HH:MM:SS string."""
    try:
        total_seconds = td.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        return "00:00:00"
