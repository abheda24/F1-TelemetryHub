import streamlit as st
import pandas as pd
import fastf1
from pathlib import Path
from data_processor import F1DataProcessor
from visualizations import F1Visualizations
from datetime import datetime
import plotly.graph_objects as go
import base64

class F1DashboardApp:
    def __init__(self):
        """Initialize the F1 Dashboard application."""
        self.setup_page_config()
        self.initialize_components()
        self.apply_custom_css()
        self.init_session_state()

    def init_session_state(self):
        """Initialize session state variables."""
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'session_data' not in st.session_state:
            st.session_state.session_data = None
        if 'selected_driver' not in st.session_state:
            st.session_state.selected_driver = None
        if 'selected_driver1' not in st.session_state:
            st.session_state.selected_driver1 = None
        if 'selected_driver2' not in st.session_state:
            st.session_state.selected_driver2 = None

    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="F1 Data Analysis Dashboard",
            page_icon="🏎️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def get_unique_key(self, base: str, *args) -> str:
        """Generate a unique key for Streamlit elements.
        
        Args:
            base (str): Base name for the key
            *args: Additional arguments to make the key unique
            
        Returns:
            str: Unique key string
        """
        key_parts = [base] + [str(arg) for arg in args if arg is not None]
        return "_".join(key_parts)    

    def initialize_components(self):
        """Initialize data processor and visualization components."""
        try:
            self.data_processor = F1DataProcessor(cache_dir='./f1_cache')
            self.visualizer = F1Visualizations()
        except Exception as e:
            st.error(f"Failed to initialize components: {str(e)}")
            st.stop()

    def get_base64_encoded_image(self, image_path):
        """Convert image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    def apply_custom_css(self):
        """Apply custom CSS styling."""
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
            
            .stApp {
                font-family: 'Titillium Web', sans-serif !important;
                background-color: #15151e !important;
                color: white;
            }
            
            .sidebar .sidebar-content {
                background-color: #15151e;
            }
            
            .stButton > button {
                width: 100%;
                background: linear-gradient(90deg, #e10600 0%, #ff1a1a 100%);
                color: white;
                font-weight: 600;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(225,6,0,0.3);
            }
            
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background-color: #1F1F1F;
                padding: 1rem;
                border-radius: 10px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: transparent;
                color: white;
                border: 1px solid #e10600;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background-color: rgba(225,6,0,0.1);
            }
            
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #e10600;
            }
            
            .stSelectbox > div {
                background-color: #1F1F1F;
                border-radius: 8px;
            }
            
            .metric-container {
                background: linear-gradient(135deg, #1F1F1F 0%, #2d2d35 100%);
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid #e10600;
            }
            
            </style>
        """, unsafe_allow_html=True)

    def load_session_data(self, year: int, gp: str, session_type: str) -> bool:
        """Load F1 session data with error handling."""
        try:
            with st.spinner("Loading session data..."):
                session_data = self.data_processor.load_session_data(
                    year=year,
                    gp=gp,
                    session_type=session_type
                )
                
                if session_data:
                    # Verify data based on test file structure
                    if (hasattr(session_data, 'session') and 
                        hasattr(session_data, 'timing') and 
                        hasattr(session_data, 'telemetry') and 
                        hasattr(session_data, 'weather') and
                        hasattr(session_data, 'driver_info') and
                        hasattr(session_data, 'event_info')):
                        
                        st.session_state.session_data = session_data
                        st.session_state.data_loaded = True
                        st.success("Data loaded successfully!")
                        return True
                    
                    else:
                        st.error("Incomplete session data structure")
                        return False
                        
            st.error("Failed to load session data")
            return False
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False

    def render_session_selection(self):
        """Render session selection sidebar."""
        try:
            encoded_logo = self.get_base64_encoded_image("assets/f1_logo.png")
            st.sidebar.markdown(f"""
                <div style='text-align: center; padding: 1rem;'>
                    <img src="data:image/png;base64,{encoded_logo}" style="width: 150px;">
                </div>
            """, unsafe_allow_html=True)
        except:
            st.sidebar.title("F1 Analysis")

        with st.sidebar:
            st.markdown("""
                <div style='text-align: center; padding: 1rem; background: #1F1F1F; border-radius: 10px; margin-bottom: 2rem;'>
                    <h2 style='color: white; margin-bottom: 0.5rem;'>Session Control</h2>
                    <div style='width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #e10600, transparent);'></div>
                </div>
            """, unsafe_allow_html=True)
            
            current_year = datetime.now().year
            year = st.selectbox(
                "Select Year",
                range(current_year, 2018, -1),
                key="year_select"
            )
            
            try:
                schedule = fastf1.get_event_schedule(year)
                gp_names = schedule['EventName'].tolist()
                
                gp = st.selectbox(
                    "Select Grand Prix",
                    gp_names,
                    key="gp_select"
                )
                
                session_types = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Sprint', 'Race']
                session_type = st.selectbox(
                    "Select Session",
                    session_types,
                    key="session_select"
                )
                
                if st.button("Load Data", key="load_button"):
                    return self.load_session_data(year, gp, session_type)
                    
            except Exception as e:
                st.error(f"Error loading schedule: {str(e)}")
                return False

    def render_event_info(self):
        """Render event information section."""
        if not st.session_state.data_loaded:
            return

        data = st.session_state.session_data
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🏁 Circuit",
                data.event_info.get('Name', 'N/A')
            )
        with col2:
            st.metric(
                "📍 Location",
                data.event_info.get('Location', 'N/A')
            )
        with col3:
            date = data.event_info.get('Date', 'N/A')
            if isinstance(date, datetime):
                date = date.strftime("%Y-%m-%d")
            st.metric("📅 Date", date)
            
    def render_lap_analysis(self):
        """Render lap analysis section."""
        if not st.session_state.data_loaded:
            st.warning("Please load session data first")
            return

        data = st.session_state.session_data
        
        # Verify timing data structure based on test file
        if not data.timing.empty:
            required_channels = [
                'Time', 'Driver', 'LapTime', 'LapNumber', 'Stint', 
                'Sector1Time', 'Sector2Time', 'Sector3Time', 'Compound'
            ]
            
            if all(channel in data.timing.columns for channel in required_channels):
                st.header("📊 Lap Time Analysis")
                
                # Lap Time Evolution
                lap_time_fig = self.visualizer.create_lap_time_chart(data.timing)
                st.plotly_chart(
                    lap_time_fig, 
                    use_container_width=True, 
                    key="lap_time_chart"
                )
                
                # Get fastest lap info for display
                fastest_lap = data.timing.sort_values('LapTime').iloc[0]
                st.markdown(f"""
                    <div style='background: #1F1F1F; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                        <h4>Fastest Lap: {fastest_lap['Driver']} - {fastest_lap['LapTime']}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                # Tyre Strategy if compound data is available
                if 'Compound' in data.timing.columns:
                    st.header("🔄 Tyre Strategy")
                    tyre_fig = self.visualizer.create_tyre_strategy(data.timing)
                    st.plotly_chart(
                        tyre_fig, 
                        use_container_width=True, 
                        key="tyre_strategy_chart"
                    )
            else:
                missing = [ch for ch in required_channels if ch not in data.timing.columns]
                st.warning(f"Missing required timing channels: {', '.join(missing)}")
        else:
            st.warning("No lap timing data available")

    def render_position_changes(self):
        """Render position changes visualization."""
        if not st.session_state.data_loaded:
            st.warning("Please load session data first")
            return

        data = st.session_state.session_data
        
        # Verify timing data has required position info
        if not data.timing.empty and 'Position' in data.timing.columns:
            st.header("🏁 Position Changes")
            
            # Add race progress info
            if 'LapNumber' in data.timing.columns:
                total_laps = data.timing['LapNumber'].max()
                st.markdown(f"""
                    <div style='background: #1F1F1F; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                        <h4>Total Laps: {total_laps}</h4>
                    </div>
                """, unsafe_allow_html=True)
            
            # Create position changes visualization
            position_fig = self.visualizer.create_position_changes_chart(data.timing)
            st.plotly_chart(
                position_fig, 
                use_container_width=True, 
                key="position_changes_chart"
            )
            
            # Add driver position summary if available
            if all(col in data.timing.columns for col in ['Driver', 'Position']):
                final_positions = data.timing.groupby('Driver')['Position'].last().sort_values()
                
                st.markdown("""
                    <div style='background: #1F1F1F; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                        <h4>Final Positions:</h4>
                """, unsafe_allow_html=True)
                
                for driver, position in final_positions.items():
                    st.markdown(f"P{int(position)}: {driver}")
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Position data not available")

    def render_weather(self):
        """Render weather analysis section."""
        if not st.session_state.data_loaded:
            st.warning("Please load session data first")
            return

        data = st.session_state.session_data
        
        # Verify weather data based on test file structure
        if not data.weather.empty:
            required_channels = [
                'Time', 'AirTemp', 'Humidity', 'Pressure',
                'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed'
            ]
            
            if all(channel in data.weather.columns for channel in required_channels):
                st.header("🌡️ Weather Conditions")
                
                # Display current conditions
                latest_weather = data.weather.iloc[-1]
                cols = st.columns(4)
                
                with cols[0]:
                    st.metric("Track Temperature", f"{latest_weather['TrackTemp']:.1f}°C")
                with cols[1]:
                    st.metric("Air Temperature", f"{latest_weather['AirTemp']:.1f}°C")
                with cols[2]:
                    st.metric("Humidity", f"{latest_weather['Humidity']:.1f}%")
                with cols[3]:
                    st.metric("Wind Speed", f"{latest_weather['WindSpeed']:.1f} km/h")
                
                # Weather trends visualization
                weather_fig = self.visualizer.create_weather_chart(data.weather)
                st.plotly_chart(
                    weather_fig, 
                    use_container_width=True, 
                    key="weather_chart"
                )
                
                # Add rainfall info if present
                if latest_weather['Rainfall'] > 0:
                    st.markdown(f"""
                        <div style='background: #1F1F1F; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                            <h4>⚠️ Rainfall Detected</h4>
                            <p>Rainfall intensity: {latest_weather['Rainfall']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                missing = [ch for ch in required_channels if ch not in data.weather.columns]
                st.warning(f"Missing required weather channels: {', '.join(missing)}")
        else:
            st.info("No weather data available for this session")        

    def render_telemetry(self):
        """Render telemetry analysis section using driver numbers."""
        if not st.session_state.data_loaded:
            st.warning("Please load session data first")
            return

        st.header("⚙️ Driver Telemetry")
        
        data = st.session_state.session_data
        
        # Create mapping between driver abbreviations and numbers
        driver_mapping = {
            
            d['abbreviation']: d['number'] for d in st.session_state.session_data.driver_info
        }
        
        
        # Driver selection using abbreviations for display
        driver_options = [d['abbreviation'] for d in st.session_state.session_data.driver_info]
        selected_driver_abbrev = st.selectbox(
            "Select Driver",
            driver_options,
            key=self.get_unique_key("telemetry_driver_select", "main")
        )
        
        # Get driver number for telemetry lookup
        selected_driver_number = str(driver_mapping.get(selected_driver_abbrev))
        
        if selected_driver_number:
            # Get team information using abbreviation
            team = next((d['team'] for d in data.driver_info 
                        if d['abbreviation'] == selected_driver_abbrev), 'Unknown')
            
            # Get telemetry data using driver number
            telemetry = data.telemetry.get(selected_driver_number, pd.DataFrame())
            
            if not telemetry.empty:
                # Verify required channels based on test file
                required_channels = ['Speed', 'RPM', 'nGear', 'DRS', 'Distance', 'Time']
                
                if all(channel in telemetry.columns for channel in required_channels):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Speed Trace")
                        speed_fig = self.visualizer.create_speed_trace(
                            telemetry,
                            selected_driver_abbrev,  # Using abbreviation for display
                            team
                        )
                        st.plotly_chart(speed_fig, use_container_width=True, 
                                    key=f"speed_trace_{selected_driver_number}")
                        
                        # Display key speed statistics
                        speed_stats = pd.DataFrame({
                            'Metric': ['Maximum Speed', 'Average Speed', 'Minimum Speed'],
                            'Value': [
                                f"{telemetry['Speed'].max():.1f} km/h",
                                f"{telemetry['Speed'].mean():.1f} km/h",
                                f"{telemetry['Speed'].min():.1f} km/h"
                            ]
                        })
                        st.dataframe(speed_stats, use_container_width=True)
                    
                    with col2:
                        st.subheader("Gear Shifts")
                        gear_fig = self.visualizer.create_gear_shifts(
                            telemetry,
                            selected_driver_abbrev,  # Using abbreviation for display
                            team
                        )
                        st.plotly_chart(gear_fig, use_container_width=True, 
                                    key=f"gear_shifts_{selected_driver_number}")
                        
                        # Display gear usage statistics
                        if 'nGear' in telemetry.columns:
                            gear_stats = telemetry['nGear'].value_counts().sort_index()
                            gear_pct = (gear_stats / len(telemetry) * 100).round(1)
                            gear_stats_df = pd.DataFrame({
                                'Count': gear_stats,
                                'Percentage': gear_pct
                            })
                            st.markdown("### Gear Usage Analysis")
                            st.dataframe(gear_stats_df, use_container_width=True)
                    
                    # Additional telemetry insights
                    st.markdown("### Additional Insights")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # DRS Usage
                        if 'DRS' in telemetry.columns:
                            drs_usage = (telemetry['DRS'].sum() / len(telemetry) * 100).round(1)
                            st.metric("DRS Usage", f"{drs_usage}%")
                    
                    with col2:
                        # RPM Statistics
                        if 'RPM' in telemetry.columns:
                            avg_rpm = telemetry['RPM'].mean().round(0)
                            max_rpm = telemetry['RPM'].max().round(0)
                            st.metric("Average RPM", f"{avg_rpm:,.0f}",
                                    delta=f"Max: {max_rpm:,.0f}")
                    
                    with col3:
                        # Distance Covered
                        if 'Distance' in telemetry.columns:
                            total_distance = telemetry['Distance'].max()
                            st.metric("Distance Covered", f"{total_distance/1000:.2f} km")
                    
                    # Time Analysis
                    if 'Time' in telemetry.columns:
                        st.markdown("### Session Timeline")
                        time_data = telemetry['Time'].dt.total_seconds()
                        session_duration = time_data.max() - time_data.min()
                        st.info(f"Session Duration: {session_duration/60:.1f} minutes")
                    
                else:
                    missing = [ch for ch in required_channels if ch not in telemetry.columns]
                    st.warning(f"Missing required telemetry channels: {', '.join(missing)}")
            else:
                st.warning(f"No telemetry data available for {selected_driver_abbrev}")
        else:
            st.error("Unable to retrieve driver information")

    def render_driver_comparison(self):
        """Render driver comparison section using driver numbers for telemetry data."""
        if not st.session_state.data_loaded:
            st.warning("Please load session data first")
            return

        st.header("🔄 Driver Comparison")
        
        data = st.session_state.session_data
        
        # Create a mapping of abbreviations to driver numbers
        driver_mapping = {
            d['abbreviation']: d['number'] for d in data.driver_info
        }
        
        # Create reverse mapping for display purposes
        number_to_abbrev = {v: k for k, v in driver_mapping.items()}
        
        # Driver selection using abbreviations for display
        col1, col2 = st.columns(2)
        driver_options = [d['abbreviation'] for d in data.driver_info]
        
        with col1:
            driver1_abbrev = st.selectbox(
                "Select First Driver",
                options=driver_options,
                key="comparison_driver1"
            )
            # Get driver number for telemetry lookup
            driver1_number = driver_mapping.get(driver1_abbrev)
            
        with col2:
            driver2_options = [d for d in driver_options if d != driver1_abbrev]
            driver2_abbrev = st.selectbox(
                "Select Second Driver",
                options=driver2_options,
                key="comparison_driver2"
            )
            # Get driver number for telemetry lookup
            driver2_number = driver_mapping.get(driver2_abbrev)
        
        if driver1_number and driver2_number:
            # Get team information using abbreviations
            team1 = next((d['team'] for d in data.driver_info 
                        if d['abbreviation'] == driver1_abbrev), 'Unknown')
            team2 = next((d['team'] for d in data.driver_info 
                        if d['abbreviation'] == driver2_abbrev), 'Unknown')
            
            # Get telemetry data using driver numbers
            telemetry1 = data.telemetry.get(str(driver1_number), pd.DataFrame())
            telemetry2 = data.telemetry.get(str(driver2_number), pd.DataFrame())
            
            # Create tabs for different comparisons
            comparison_tabs = st.tabs([
                "Speed Comparison",
                "Gear Usage",
                "Speed Traces",
                "Detailed Analysis"
            ])
            
            with comparison_tabs[0]:
                if (not telemetry1.empty and not telemetry2.empty and
                    'Speed' in telemetry1.columns and 'Speed' in telemetry2.columns and
                    'Distance' in telemetry1.columns and 'Distance' in telemetry2.columns):
                    
                    comparison_fig = self.visualizer.create_driver_comparison(
                        telemetry1,
                        telemetry2,
                        driver1_abbrev,
                        driver2_abbrev,
                        team1,
                        team2
                    )
                    st.plotly_chart(comparison_fig, use_container_width=True, 
                                key=f"speed_comparison_{driver1_number}_{driver2_number}")
                else:
                    st.warning("Required telemetry data not available for speed comparison")
            
            with comparison_tabs[1]:
                col1, col2 = st.columns(2)
                with col1:
                    if not telemetry1.empty and 'nGear' in telemetry1.columns and 'Distance' in telemetry1.columns:
                        gear_fig1 = self.visualizer.create_gear_shifts(
                            telemetry1,
                            driver1_abbrev,
                            team1
                        )
                        st.plotly_chart(gear_fig1, use_container_width=True,
                                    key=f"gear_shifts_{driver1_number}")
                    else:
                        st.warning(f"Gear data not available for {driver1_abbrev}")
                        
                with col2:
                    if not telemetry2.empty and 'nGear' in telemetry2.columns and 'Distance' in telemetry2.columns:
                        gear_fig2 = self.visualizer.create_gear_shifts(
                            telemetry2,
                            driver2_abbrev,
                            team2
                        )
                        st.plotly_chart(gear_fig2, use_container_width=True,
                                    key=f"gear_shifts_{driver2_number}")
                    else:
                        st.warning(f"Gear data not available for {driver2_abbrev}")
            
            with comparison_tabs[2]:
                col1, col2 = st.columns(2)
                with col1:
                    if not telemetry1.empty and 'Speed' in telemetry1.columns and 'Distance' in telemetry1.columns:
                        speed_fig1 = self.visualizer.create_speed_trace(
                            telemetry1,
                            driver1_abbrev,
                            team1
                        )
                        st.plotly_chart(speed_fig1, use_container_width=True,
                                    key=f"speed_trace_{driver1_number}")
                    else:
                        st.warning(f"Speed trace data not available for {driver1_abbrev}")
                        
                with col2:
                    if not telemetry2.empty and 'Speed' in telemetry2.columns and 'Distance' in telemetry2.columns:
                        speed_fig2 = self.visualizer.create_speed_trace(
                            telemetry2,
                            driver2_abbrev,
                            team2
                        )
                        st.plotly_chart(speed_fig2, use_container_width=True,
                                    key=f"speed_trace_{driver2_number}")
                    else:
                        st.warning(f"Speed trace data not available for {driver2_abbrev}")
            
            with comparison_tabs[3]:
                if not telemetry1.empty and not telemetry2.empty:
                    col1, col2 = st.columns(2)
                    
                    # Speed statistics
                    with col1:
                        st.markdown("### Speed Analysis")
                        if 'Speed' in telemetry1.columns and 'Speed' in telemetry2.columns:
                            stats_df = pd.DataFrame({
                                driver1_abbrev: [
                                    f"{telemetry1['Speed'].max():.1f}",
                                    f"{telemetry1['Speed'].mean():.1f}",
                                    f"{telemetry1['Speed'].std():.1f}"
                                ],
                                driver2_abbrev: [
                                    f"{telemetry2['Speed'].max():.1f}",
                                    f"{telemetry2['Speed'].mean():.1f}",
                                    f"{telemetry2['Speed'].std():.1f}"
                                ]
                            }, index=['Max Speed (km/h)', 'Avg Speed (km/h)', 'Speed Variation'])
                            st.dataframe(stats_df, use_container_width=True)
                        else:
                            st.warning("Speed data not available for analysis")
                    
                    # Gear usage statistics
                    with col2:
                        if 'nGear' in telemetry1.columns and 'nGear' in telemetry2.columns:
                            st.markdown("### Gear Usage")
                            gear_stats = pd.DataFrame({
                                driver1_abbrev: telemetry1['nGear'].value_counts(normalize=True),
                                driver2_abbrev: telemetry2['nGear'].value_counts(normalize=True)
                            }).fillna(0) * 100
                            gear_stats = gear_stats.round(1)
                            st.dataframe(gear_stats, use_container_width=True)
                        else:
                            st.warning("Gear usage data not available")
                    
                    # Speed differential
                    if all(col in telemetry1.columns for col in ['Speed', 'Distance']) and \
                    all(col in telemetry2.columns for col in ['Speed', 'Distance']):
                        st.markdown("### Speed Differential Analysis")
                        
                        # Prepare data for analysis
                        data1 = telemetry1[['Distance', 'Speed']].sort_values('Distance')
                        data2 = telemetry2[['Distance', 'Speed']].sort_values('Distance')
                        
                        merged_data = pd.merge_asof(
                            data1, data2,
                            on='Distance',
                            suffixes=('_1', '_2')
                        )
                        
                        speed_delta = merged_data['Speed_1'] - merged_data['Speed_2']
                        
                        diff_stats = pd.DataFrame({
                            'Metric': ['Maximum Advantage', 'Average Difference', 'Standard Deviation'],
                            'Value': [
                                f"{speed_delta.abs().max():.1f} km/h",
                                f"{speed_delta.mean():.1f} km/h",
                                f"{speed_delta.std():.1f} km/h"
                            ],
                            'Favors': [
                                driver1_abbrev if speed_delta.max() > 0 else driver2_abbrev,
                                driver1_abbrev if speed_delta.mean() > 0 else driver2_abbrev,
                                'N/A'
                            ]
                        })
                        st.dataframe(diff_stats, use_container_width=True)
                    else:
                        st.warning("Required data for speed differential analysis not available")
                else:
                    st.warning("Detailed analysis requires valid telemetry data for both drivers")

    def run(self):
        """Main application execution."""
        try:
            encoded_logo = self.get_base64_encoded_image("assets/f1_logo.png")
            st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 2rem;">
                    <img src="data:image/png;base64,{encoded_logo}" style="height: 60px; margin-right: 20px;">
                    <h1 style="color: white; margin: 0;">Data Analysis Dashboard</h1>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.title("F1 Data Analysis Dashboard")
        
        # Render session selection sidebar
        data_loaded = self.render_session_selection()
        
        # Only render main content if data is loaded
        if st.session_state.data_loaded:
            self.render_event_info()
            
            tabs = st.tabs([
                "📊 Lap Analysis",
                "🏁 Race Position",
                "⚙️ Telemetry",
                "🌡️ Weather",
                "🔄 Driver Comparison"
            ])
            
            with tabs[0]:
                self.render_lap_analysis()
            with tabs[1]:
                self.render_position_changes()
            with tabs[2]:
                self.render_telemetry()
            with tabs[3]:
                self.render_weather()
            with tabs[4]:
                self.render_driver_comparison()

if __name__ == "__main__":
    app = F1DashboardApp()
    app.run()