#!/bin/bash

# Hacksara Earthquake Detection POC Setup Script
# This script sets up the environment and downloads sample data

set -e  # Exit on any error

echo "🌍 Hacksara Earthquake Detection POC Setup"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/plots
mkdir -p logs
mkdir -p data/earthquake_events

# Download sample data if it doesn't exist
if [ ! -f "data/sample_imu_data.csv" ]; then
    echo "📥 Downloading sample IMU data..."
    curl -L -o data/sample_imu_data.csv "https://raw.githubusercontent.com/hacksara/earthquake-detection-poc/main/data/sample_imu_data.csv"
    echo "✅ Sample data downloaded"
else
    echo "✅ Sample data already exists"
fi

# Download earthquake data if it doesn't exist
if [ ! -f "data/earthquake_data_summary.json" ]; then
    echo "📥 Downloading earthquake data..."
    curl -L -o data/earthquake_data_summary.json "https://raw.githubusercontent.com/hacksara/earthquake-detection-poc/main/data/earthquake_data_summary.json"
    echo "✅ Earthquake data summary downloaded"
else
    echo "✅ Earthquake data summary already exists"
fi

# Create .env file with default settings
echo "⚙️  Creating .env file..."
cat > .env << EOF
# Earthquake Detection Configuration

# Detection Parameters
EARTHQUAKE_PGA_THRESHOLD=0.02
EARTHQUAKE_PGA_CONFIRMATION=0.05
EARTHQUAKE_STA_LTA_THRESHOLD=2.5
EARTHQUAKE_MIN_DURATION_SECONDS=0.5

# Filtering Parameters
EARTHQUAKE_LOW_CUT_FREQ=0.5
EARTHQUAKE_HIGH_CUT_FREQ=5.0
EARTHQUAKE_FILTER_ORDER=4

# Processing Parameters
EARTHQUAKE_STA_WINDOW_SECONDS=1.0
EARTHQUAKE_LTA_WINDOW_SECONDS=10.0
EARTHQUAKE_SAMPLE_RATE=104

# Output Settings
EARTHQUAKE_SAVE_DETECTION_PLOTS=true
EARTHQUAKE_PLOT_DIRECTORY=data/plots

# Logging
EARTHQUAKE_LOG_LEVEL=INFO
EARTHQUAKE_LOG_FILE=logs/earthquake_detector.log

# Data Processing
EARTHQUAKE_CHUNK_SIZE=1000
EARTHQUAKE_OVERLAP_SECONDS=1.0

# Advanced Settings
EARTHQUAKE_ENABLE_DEBUG_MODE=false
EARTHQUAKE_MAX_PROCESSING_TIME=30.0
EOF

echo "✅ .env file created with default settings"

# Test the installation
echo "🧪 Testing installation..."
python3 -c "import numpy, scipy, pandas, matplotlib; print('✅ Core dependencies working')"

# Test the earthquake detection system
echo "🧪 Testing earthquake detection system..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from earthquake_detector import EarthquakeDetector
from config import Settings
detector = EarthquakeDetector()
print('✅ Earthquake detection system working')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Run the demo: python scripts/demo_detection.py"
echo "   3. Test with real data: python scripts/demo_detection.py --test-all-files"
echo "   4. Generate plots: python scripts/plot_earthquakes.py"
echo ""
echo "📚 Documentation:"
echo "   - README.md: Main documentation"
echo "   - QUICKSTART.md: Quick start guide"
echo "   - docs/technical_spec.md: Technical specifications"
echo ""
echo "🔧 Configuration:"
echo "   - Edit .env file to customize settings"
echo "   - Modify src/config.py for advanced configuration"
echo ""
echo "🌍 Happy earthquake detecting!" 