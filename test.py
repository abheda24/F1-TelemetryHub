# test_data_processor.py

import pandas as pd
import logging
from data_processor import F1DataProcessor
import fastf1

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_session_loading():
    """Test basic session loading functionality."""
    try:
        print("\n=== Testing Session Loading ===")
        processor = F1DataProcessor(cache_dir='./cache')
        
        # Test a known good session (2023 Monaco GP Qualifying)
        year = 2023
        gp = 'Monaco'
        session_type = 'Q'
        
        print(f"\nLoading {year} {gp} {session_type} session...")
        session_data = processor.load_session_data(year, gp, session_type)
        
        # Check all components
        print("\nChecking session components:")
        print(f"Session loaded: {session_data.session is not None}")
        print(f"Timing data available: {not session_data.timing.empty}")
        print(f"Number of drivers with telemetry: {len(session_data.telemetry)}")
        print(f"Weather data available: {not session_data.weather.empty}")
        print(f"Track status data available: {not session_data.track_status.empty}")
        print(f"Race control messages available: {not session_data.race_control.empty}")
        print(f"Number of drivers in info: {len(session_data.driver_info)}")
        print(f"Event info available: {bool(session_data.event_info)}")
        
        return session_data
        
    except Exception as e:
        print(f"Error in session loading test: {e}")
        return None

def test_telemetry_data(session_data):
    """Test telemetry data extraction and processing."""
    try:
        print("\n=== Testing Telemetry Data ===")
        
        if session_data and session_data.telemetry:
            # Get first driver's telemetry
            driver = list(session_data.telemetry.keys())[0]
            telemetry = session_data.telemetry[driver]
            
            print(f"\nTelemetry data for driver {driver}:")
            print("Available channels:", telemetry.columns.tolist())
            print("Number of data points:", len(telemetry))
            
            # Check for key telemetry channels
            key_channels = ['Speed', 'RPM', 'nGear', 'DRS', 'Distance']
            for channel in key_channels:
                print(f"{channel} data available: {channel in telemetry.columns}")
        else:
            print("No telemetry data available for testing")
            
    except Exception as e:
        print(f"Error in telemetry test: {e}")

def test_driver_info(session_data):
    """Test driver information extraction."""
    try:
        print("\n=== Testing Driver Information ===")
        
        if session_data and session_data.driver_info:
            print(f"\nNumber of drivers: {len(session_data.driver_info)}")
            
            # Print information for first driver
            first_driver = session_data.driver_info[0]
            print("\nFirst driver information:")
            for key, value in first_driver.items():
                print(f"{key}: {value}")
                
            # Check all drivers have required fields
            required_fields = ['number', 'abbreviation', 'fullname', 'team', 'team_color']
            all_fields_present = all(
                all(field in driver for field in required_fields)
                for driver in session_data.driver_info
            )
            print(f"\nAll required fields present: {all_fields_present}")
        else:
            print("No driver information available for testing")
            
    except Exception as e:
        print(f"Error in driver info test: {e}")

def test_event_info(session_data):
    """Test event information extraction."""
    try:
        print("\n=== Testing Event Information ===")
        
        if session_data and session_data.event_info:
            print("\nAvailable event information:")
            for key, value in session_data.event_info.items():
                print(f"{key}: {value}")
                
            # Check for key event information
            key_info = ['Name', 'Country', 'Location', 'SessionType', 'Date']
            for info in key_info:
                print(f"{info} available: {info in session_data.event_info}")
        else:
            print("No event information available for testing")
            
    except Exception as e:
        print(f"Error in event info test: {e}")

def test_timing_data(session_data):
    """Test timing data processing."""
    try:
        print("\n=== Testing Timing Data ===")
        
        if session_data and not session_data.timing.empty:
            print(f"\nNumber of laps: {len(session_data.timing)}")
            print("Available timing channels:", session_data.timing.columns.tolist())
            
            # Check for key timing information
            key_timing = ['Driver', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Compound']
            for info in key_timing:
                print(f"{info} data available: {info in session_data.timing.columns}")
                
            # Print fastest lap info
            fastest_lap = session_data.timing.sort_values('LapTime').iloc[0]
            print(f"\nFastest lap by {fastest_lap['Driver']}: {fastest_lap['LapTime']}")
        else:
            print("No timing data available for testing")
            
    except Exception as e:
        print(f"Error in timing test: {e}")

def test_weather_data(session_data):
    """Test weather data processing."""
    try:
        print("\n=== Testing Weather Data ===")
        
        if session_data and not session_data.weather.empty:
            print(f"\nNumber of weather records: {len(session_data.weather)}")
            print("Available weather channels:", session_data.weather.columns.tolist())
            
            # Check for key weather information
            key_weather = ['AirTemp', 'Humidity', 'Pressure', 'Rainfall', 'TrackTemp']
            for info in key_weather:
                print(f"{info} data available: {info in session_data.weather.columns}")
        else:
            print("No weather data available for testing")
            
    except Exception as e:
        print(f"Error in weather test: {e}")

def run_all_tests():
    """Run all tests sequentially."""
    try:
        print("Starting comprehensive data processor testing...")
        
        # Load session data first
        session_data = test_session_loading()
        
        if session_data:
            # Run all other tests
            test_telemetry_data(session_data)
            test_driver_info(session_data)
            test_event_info(session_data)
            test_timing_data(session_data)
            test_weather_data(session_data)
            
            print("\n=== Testing Complete ===")
        else:
            print("Testing stopped due to session loading failure")
            
    except Exception as e:
        print(f"Error in test suite: {e}")

if __name__ == "__main__":
    run_all_tests()