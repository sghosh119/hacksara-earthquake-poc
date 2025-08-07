# 🌍 Hacksara Earthquake Detection POC

A proof-of-concept earthquake detection system using IMU accelerometer data. This demo showcases real-time earthquake detection capabilities for gas pipeline safety applications.

## 🚀 Quick Start

```bash
# Setup environment
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run the demo
python scripts/demo_detection.py --full-demo
```

## 🎯 Demo Features

- **Real Earthquake Data**: 1,567 real earthquakes from USGS API
- **Multi-category Testing**: Big (M5.1+), borderline (M4.5-5.0), and small (M4.0-4.4) earthquakes
- **Detection Algorithm**: PGA + STA/LTA analysis
- **Visualization**: Comprehensive analysis plots
- **Streamlined Workflow**: Focused on real-world scenarios

## 📁 Project Structure

```
hacksara-earthquake-poc/
├── scripts/
│   ├── demo_detection.py          # 🎯 MAIN DEMO SCRIPT
│   ├── fetch_earthquake_data.py   # USGS data fetching
│   └── plot_earthquakes.py        # Analysis plotting
├── src/                           # Core detection logic
│   ├── earthquake_detector.py     # Main detection algorithm
│   ├── filters.py                 # Signal processing
│   ├── config.py                  # Configuration
│   └── utils.py                   # Utilities
├── data/                          # Sample data and results
│   ├── plots/                     # Generated plots
│   └── *.csv                      # Real earthquake data files
├── docs/                          # Technical documentation
├── QUICKSTART.md                  # Detailed setup guide
└── setup.sh                       # Environment setup
```

## 🎮 Demo Commands

```bash
# Complete demo workflow
python scripts/demo_detection.py --full-demo

# Individual components
python scripts/demo_detection.py --fetch-data
python scripts/demo_detection.py --create-plots
python scripts/demo_detection.py --test-all-files

# Test specific file
python scripts/demo_detection.py --data-file data/big_M6.8_118_km__E_of_Severo-Kuril'sk_R_20250802_2237.csv

# Test with sample data (default)
python scripts/demo_detection.py
```

## 🔬 Detection Algorithm

- **PGA Analysis**: Peak Ground Acceleration detection
- **STA/LTA Ratio**: Short-term/Long-term average analysis
- **Bandpass Filtering**: 0.5-5.0 Hz seismic frequencies
- **Multi-criteria Decision**: Combined detection logic
- **Confidence Scoring**: 0-3 point scale
- **Duration Filtering**: Sustained shaking detection

## 📊 Demo Output

The demo generates:
- Real-time detection results
- Comprehensive analysis plots
- Detection statistics
- Real earthquake data testing

## 🛡️ Safety Notes

⚠️ **This is a proof-of-concept for demonstration purposes.**

- Seismic gas valves are mechanical and RF-immune
- VG55 devices emit <100mW (safe for gas environments)
- Proper installation requires professional assessment
- Compliance with local codes and regulations required

## 📖 Documentation

- **QUICKSTART.md**: Complete setup and demo guide
- **docs/technical_spec.md**: Technical implementation details
- **scripts/README.md**: Script organization guide

---

**Happy Demo-ing! 🚀**

For questions or issues, refer to QUICKSTART.md for detailed instructions.
