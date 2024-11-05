# 🏎️ F1 Data Analysis Dashboard

A comprehensive Formula 1 data analysis platform leveraging real-time telemetry data to provide deep insights into race performance, driver comparisons, and technical analysis.

![F1 Dashboard](assets/f1_logo.png)

## 📊 Features

- **Real-time Telemetry Analysis**
  - Speed traces
  - Gear shift patterns
  - DRS usage analysis
  - RPM monitoring

- **Race Performance Analytics**
  - Lap time evolution
  - Position changes visualization
  - Tire strategy analysis
  - Sector time comparisons

- **Driver Comparisons**
  - Head-to-head speed analysis
  - Gear usage patterns
  - Performance differentials
  - Detailed statistical analysis

- **Weather Integration**
  - Track temperature monitoring
  - Weather condition impacts
  - Real-time updates
  - Historical weather data

## 🛠️ Technology Stack

- **Backend**
  - Python 3.8+
  - FastF1 API
  - Pandas
  - NumPy

- **Frontend**
  - Streamlit
  - Plotly
  - Seaborn
  - Matplotlib

- **Data Processing**
  - Real-time telemetry processing
  - Custom data validation
  - Cache management
  - Error handling

## 📁 Project Structure

```
f1-analytics/
├── app.py                 # Main Streamlit application
├── data_processor.py      # Data processing module
├── visualizations.py      # Visualization components
├── test.py               # Test suite
├── requirements.txt      # Project dependencies
├── .gitignore           # Git ignore configuration
├── README.md            # Project documentation
├── assets/              # Static resources
│   └── f1_logo.png     # F1 logo
└── cache/              # Data cache directory
```

## 🚦 Getting Started

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/f1-analytics.git
cd f1-analytics
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Application**
```bash
streamlit run app.py
```

## 📦 Requirements

Create a `requirements.txt` file with:
```
fastf1==3.3.9
streamlit==1.31.0
plotly==5.18.0
pandas==2.2.0
numpy==1.26.3
seaborn==0.13.1
matplotlib==3.8.2
```


## 🔧 Configuration

Key configuration settings are managed through environment variables:
- `CACHE_DIR`: Directory for FastF1 cache (default: './cache')
- `DEBUG`: Enable debug mode (default: False)

## 📊 Data Processing

The application processes various types of F1 data:
- Telemetry data (speed, RPM, gears)
- Timing data (lap times, sectors)
- Position data
- Weather conditions

### Key Modules

1. **Data Processor (`data_processor.py`)**
   - FastF1 API integration
   - Data validation
   - Cache management

2. **Visualizations (`visualizations.py`)**
   - Custom plotting functions
   - Interactive charts
   - Real-time updates

3. **Main App (`app.py`)**
   - Streamlit interface
   - User interactions
   - Data presentation

## 🧪 Testing

Run the test suite:
```bash
python test.py
```

The test suite covers:
- Data loading
- Telemetry processing
- Visualization generation
- Error handling

## 💻 Usage Examples

```python
# Load session data
session_data = data_processor.load_session_data(2024, "Bahrain", "Race")

# Create speed trace
speed_trace = visualizer.create_speed_trace(
    telemetry_data,
    driver="VER",
    team="Red Bull Racing"
)
```

## 📈 Performance Considerations

- Caching implementation for faster data retrieval
- Optimized data processing for real-time analysis
- Efficient memory management for large datasets

## 👨‍💻 Author

Akshay Bheda
- GitHub: [@abheda24](https://github.com/abheda24)
- LinkedIn: [Akshay Bheda](https://linkedin.com/in/akshay-bheda9630)

