# 🚀 Quick Start Guide - Hacksara Earthquake Detection POC

This guide will get you up and running with the earthquake detection demo in minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- Terminal/Command Prompt

## Step 1: Setup Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd hacksara-earthquake-poc

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Generate sample data
- ✅ Set up project structure

## Step 2: Activate Virtual Environment

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

## Step 3: Run the Demo

### Option A: Full Demo (Recommended)

```bash
python scripts/demo_detection.py --full-demo
```

This comprehensive demo will:
- 📥 Fetch real earthquake data from USGS API
- 🔍 Test detection with all earthquake files
- 📊 Create comprehensive analysis plots
- 📈 Show detailed results and statistics

### Option B: Individual Components

#### Fetch New Earthquake Data
```bash
python scripts/demo_detection.py --fetch-data
```

#### Create Analysis Plots
```bash
python scripts/demo_detection.py --create-plots
```

#### Test All Earthquake Files
```bash
python scripts/demo_detection.py --test-all-files
```

#### Test with Specific File
```bash
python scripts/demo_detection.py --data-file data/big_M6.8_118_km__E_of_Severo-Kuril'sk_R_20250802_2237.csv
```

#### Test with Sample Data (Default)
```bash
python scripts/demo_detection.py
```

## Demo Features

### 🌍 Earthquake Detection Algorithm
- **Bandpass Filtering**: 0.5-5.0 Hz seismic frequencies
- **PGA Analysis**: Peak Ground Acceleration detection
- **STA/LTA Ratio**: Short-term/Long-term average analysis
- **Duration Filter**: Sustained shaking detection
- **Multi-criteria Decision**: Combined detection logic

### 📊 Detection Parameters
- **PGA Threshold**: 0.02g (initial alert)
- **PGA Confirmation**: 0.05g (strong confirmation)
- **STA/LTA Threshold**: 2.5
- **Min Duration**: 0.5 seconds
- **Sample Rate**: 104 Hz

### 🎯 Detection Criteria
1. **PGA Check**: Acceleration exceeds threshold
2. **STA/LTA Check**: Signal amplitude ratio exceeds threshold
3. **Duration Check**: Sustained shaking for minimum time
4. **Confidence Scoring**: 0-3 point scale

## Example Output

```
🌍 Earthquake Detection Demo
==================================================
🚀 Running Complete Demo Workflow
==================================================

📥 Step 1: Fetching earthquake data from USGS API...
📥 Fetching earthquake data from USGS API...
📊 Found 15 earthquakes:
   1. M6.8 - 118 km E of Severo-Kuril'sk, Russia (2025-08-02 22:37)
   2. M6.9 - 133 km SE of Petropavlovsk-Kamchatsky, Russia (2025-07-29 17:09)
   3. M6.9 - Macquarie Island region (2025-07-28 15:10)
   4. M5.0 - 140 km ESE of Ozernovskiy, Russia (2025-08-04 14:06)
   5. M5.0 - 144 km SSE of Vilyuchinsk, Russia (2025-08-04 04:37)

📂 Categorizing earthquakes:
   - Big earthquakes (M≥5.1): 3
   - Borderline earthquakes (M4.5-5.0): 2
   - Small earthquakes (M<4.5): 10

🔍 Step 2: Testing earthquake detection...
📊 Testing with all earthquake data files
   Found 9 earthquake data files

📈 Testing BIG earthquakes (3 files)
   📊 Processing: big_M6.8_118_km__E_of_Severo-Kuril'sk_R_20250802_2237.csv
   ✅ EARTHQUAKE DETECTED!
   📊 Processing: big_M6.9_133_km__SE_of_Petropavlovsk-Ka_20250729_1709.csv
   ✅ EARTHQUAKE DETECTED!

📊 Step 3: Creating analysis plots...
📊 Creating comprehensive earthquake plots...
📈 Creating plots for BIG earthquakes...
   📊 Processing: big_M6.8_118_km__E_of_Severo-Kuril'sk_R_20250802_2237.csv
   📍 M6.8 - 118 km E of Severo-Kuril'sk, Russia
   ✅ Saved: big_M6.8_test1_analysis.png

📊 Final Statistics:
   Total Detections: 5
   Last Detection: 2025-01-15 10:30:45.123456

🎉 Full demo workflow completed!
```

## Configuration

### Command Line Options
- `--full-demo`: Run complete demo workflow
- `--fetch-data`: Fetch new earthquake data from USGS API
- `--create-plots`: Create comprehensive earthquake analysis plots
- `--test-all-files`: Test all earthquake data files
- `--data-file`: Test with specific data file
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Environment Variables
Copy the template and customize:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Key Parameters
- `DETECTION_PGA_THRESHOLD`: Initial detection threshold
- `DETECTION_STA_LTA_THRESHOLD`: Signal ratio threshold
- `SAVE_DETECTION_PLOTS`: Save visualization plots

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Detection Plots Not Generating**
   ```bash
   # Check plot directory permissions
   ls -la data/plots/
   ```

3. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   ```

### Getting Help

- 📖 Check the technical documentation: `docs/technical_spec.md`
- 🧪 Run tests: `python -m pytest tests/`
- 📝 View logs: `logs/earthquake_detector.log`

## Next Steps

### For Hackathon Demo
1. ✅ Run the full demo: `python scripts/demo_detection.py --full-demo`
2. ✅ Show individual components
3. ✅ Explain the detection algorithm
4. ✅ Demonstrate confidence scoring
5. ✅ Show detection plots and analysis

### For Development
1. 🔧 Customize detection parameters
2. 📊 Analyze different earthquake scenarios
3. 🧪 Add new test cases
4. 📈 Improve detection accuracy
5. 🔗 Integrate with real VG55 data

## Project Structure

```
hacksara-earthquake-poc/
├── README.md              # Main documentation
├── QUICKSTART.md          # This file
├── requirements.txt       # Python dependencies
├── setup.sh              # Environment setup
├── src/                  # Source code
│   ├── config.py         # Configuration management
│   ├── filters.py        # Signal processing
│   ├── earthquake_detector.py  # Main detection logic
│   └── utils.py          # Utilities and helpers
├── scripts/              # Demo and utility scripts
│   ├── demo_detection.py # Main demo script (entry point)
│   ├── fetch_earthquake_data.py # USGS data fetching
│   └── plot_earthquakes.py # Analysis plotting
├── tests/                # Test files
├── data/                 # Sample data and results
└── docs/                 # Technical documentation
```

## Script Organization

### Main Demo Script (`demo_detection.py`)
- **Entry point** for all demo functionality
- Orchestrates calls to other scripts
- Handles command line arguments
- Provides comprehensive logging

### Data Fetching (`fetch_earthquake_data.py`)
- Fetches real earthquake data from USGS API
- Converts to IMU format for testing
- Categorizes earthquakes (big, borderline, small)
- Saves data with metadata

### Plotting (`plot_earthquakes.py`)
- Creates comprehensive earthquake analysis plots
- Generates comparison visualizations
- Saves plots to `data/plots/` directory

## Safety Notes

⚠️ **Important**: This is a proof of concept for demonstration purposes.

- 🔒 Seismic gas valves are mechanical and RF-immune
- 📡 VG55 devices emit <100mW (safe for gas environments)
- 🏠 Proper installation requires professional assessment
- 📋 Compliance with local codes and regulations required

---

**Happy Demo-ing! 🚀**

For questions or issues, refer to the main README.md or technical documentation. 