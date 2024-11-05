# data_processor.py

import fastf1
import fastf1.plotting
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Container for session data following FastF1 structure."""
    session: fastf1.core.Session  # Raw session object
    timing: pd.DataFrame         # Lap timing data (from session.laps)
    telemetry: Dict[str, pd.DataFrame]  # Car telemetry data for each driver
    weather: pd.DataFrame        # Weather conditions (from session.weather_data)
    track_status: pd.DataFrame   # Track status updates (from session.track_status)
    race_control: pd.DataFrame   # Race control messages (from session.race_control_messages)
    driver_info: List[Dict[str, str]]  # Driver information from session results
    event_info: Dict[str, Any]   # Event information from session.event

class F1DataProcessor:
    """Process and manage F1 session data using FastF1."""

    def __init__(self, cache_dir: str = './cache'):
        """Initialize F1DataProcessor with caching enabled."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Enable FastF1 caching
        fastf1.Cache.enable_cache(str(self.cache_dir))
        
        # Enable plotting setup
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False)
        
        logger.info(f"Initialized F1DataProcessor with cache at '{self.cache_dir.resolve()}'")

    def load_session_data(self, year: int, gp: str, session_type: str) -> SessionData:
        """Load complete session data."""
        try:
            # Get and load session
            session = fastf1.get_session(year, gp, session_type)
            session.load(laps=True, telemetry=True, weather=True, messages=True)
            
            # Get timing data
            timing = session.laps.copy()
            
            # Get telemetry data
            telemetry = self._get_telemetry_data(session)
            
            # Get driver information
            driver_info = self._get_driver_info(session)
            
            # Get event information
            event_info = self._get_event_info(session)
            
            # Create session data container
            session_data = SessionData(
                session=session,
                timing=timing,
                telemetry=telemetry,
                weather=session.weather_data if hasattr(session, 'weather_data') else pd.DataFrame(),
                track_status=session.track_status if hasattr(session, 'track_status') else pd.DataFrame(),
                race_control=session.race_control_messages if hasattr(session, 'race_control_messages') else pd.DataFrame(),
                driver_info=driver_info,
                event_info=event_info
            )
            
            logger.info(f"Successfully loaded session data for {year} {gp} {session_type}")
            return session_data
        
        except Exception as e:
            logger.error(f"Error loading session data: {str(e)}")
            raise

    def _get_driver_info(self, session: fastf1.core.Session) -> List[Dict[str, str]]:
        """
        Extract driver information from session results.
        """
        drivers_info = []
        try:
            if hasattr(session, 'results'):
                results_df = session.results
                
                # Process each driver from the results DataFrame
                for _, driver in results_df.iterrows():
                    driver_info = {
                        'number': str(driver['DriverNumber']),
                        'abbreviation': driver['Abbreviation'],
                        'fullname': driver['FullName'],
                        'team': driver['TeamName'],
                        'team_color': driver['TeamColor']  # Use TeamColor directly from results
                    }
                    drivers_info.append(driver_info)
                    
                logger.info(f"Successfully extracted information for {len(drivers_info)} drivers from results")
                return drivers_info
                
            # Fallback to drivers list if results not available
            for driver_number in session.drivers:
                try:
                    driver_data = session.get_driver(driver_number)
                    if driver_data is not None:
                        driver_info = {
                            'number': str(driver_number),
                            'abbreviation': driver_data.Abbreviation,
                            'fullname': f"{driver_data.FirstName} {driver_data.LastName}",
                            'team': driver_data.TeamName,
                            'team_color': fastf1.plotting.team_color(driver_data.TeamName)
                        }
                        drivers_info.append(driver_info)
                except Exception as e:
                    logger.warning(f"Could not get info for driver {driver_number}: {str(e)}")
                    continue
                    
            logger.info(f"Successfully extracted information for {len(drivers_info)} drivers from drivers list")
            return drivers_info
            
        except Exception as e:
            logger.error(f"Error getting driver information: {str(e)}")
            return []

    def _get_event_info(self, session: fastf1.core.Session) -> Dict[str, Any]:
        """
        Extract event information from session.
        """
        try:
            event_info = {}
            
            # Get event information
            if hasattr(session, 'event'):
                event = session.event
                event_info.update({
                    'Name': event['EventName'],
                    'Country': event['Country'],
                    'Location': event['Location'],
                    'OfficialName': event['OfficialEventName'],
                    'F1ApiSupport': event['F1ApiSupport']
                })

            # Get circuit information
            try:
                circuit_info = session.get_circuit_info()
                if circuit_info and hasattr(circuit_info, 'corners'):
                    # Take the actual circuit length value
                    circuit_length = circuit_info.corners['Distance'].max()
                    event_info['CircuitLength'] = circuit_length
            except Exception as e:
                logger.warning(f"Could not get circuit info: {str(e)}")

            # Get session information
            event_info.update({
                'Date': session.date,
                'SessionType': session.name,
                'WeekendSessionType': session.weekend_session_type if hasattr(session, 'weekend_session_type') else None,
            })

            # Filter out None values
            event_info = {k: v for k, v in event_info.items() if v is not None}
            
            logger.info("Successfully extracted event information")
            return event_info
            
        except Exception as e:
            logger.error(f"Error getting event information: {str(e)}")
            return {}

    def get_event_by_name(self, schedule: pd.DataFrame, name: str) -> pd.Series:
        """Get event by exact name match."""
        try:
            return schedule[schedule['EventName'].str.lower() == name.lower()].iloc[0]
        except IndexError:
            logger.error(f"No event found matching name '{name}'")
            return pd.Series()

    def get_event_by_round(self, schedule: pd.DataFrame, round_number: int) -> pd.Series:
        """Get event by round number."""
        try:
            return schedule[schedule['RoundNumber'] == round_number].iloc[0]
        except IndexError:
            logger.error(f"No event found for round number {round_number}")
            return pd.Series()
        
    def _get_telemetry_data(self, session: fastf1.core.Session) -> Dict[str, pd.DataFrame]:
        """Get telemetry data for each driver's fastest lap."""
        telemetry_data = {}
        try:
            for driver in session.drivers:
                try:
                    driver_laps = session.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        fastest_lap = driver_laps.pick_fastest()
                        if fastest_lap is not None:
                            # Get car data
                            car_data = fastest_lap.get_car_data()
                            if not car_data.empty:
                                # Add distance channel
                                if 'Distance' not in car_data.columns:
                                    car_data = car_data.copy()
                                    car_data['Distance'] = car_data['Time'].dt.total_seconds() * car_data['Speed'] / 3.6
                                telemetry_data[driver] = car_data
                                
                except Exception as e:
                    logger.warning(f"Could not get telemetry for driver {driver}: {str(e)}")
                    continue
            
            return telemetry_data
        except Exception as e:
            logger.error(f"Error processing telemetry data: {str(e)}")
            return {}    