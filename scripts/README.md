# Scripts Directory

This directory contains the main demo and utility scripts for the earthquake detection system.

## Script Organization

### 🎯 Main Entry Point: `demo_detection.py`

**Purpose**: Main demo script that orchestrates all functionality

**Usage**:
```bash
# Run complete demo workflow
python scripts/demo_detection.py --full-demo

# Individual components
python scripts/demo_detection.py --fetch-data
python scripts/demo_detection.py --create-plots
python scripts/demo_detection.py --test-synthetic
python scripts/demo_detection.py --test-all-files
```

**Features**:
- Orchestrates calls to other scripts
- Handles command line arguments
- Provides comprehensive logging
- Entry point for all demo functionality

### 📥 Data Fetching: `fetch_earthquake_data.py`

**Purpose**: Fetch real earthquake data from USGS API and convert to IMU format

**Key Functions**:
- `fetch_usgs_earthquakes()`: Fetch from USGS API
- `convert_earthquake_to_imu_data()`: Convert to IMU format
- `categorize_earthquakes()`: Sort into big/borderline/small
- `save_earthquake_data()`: Save with metadata

**Called by**: `demo_detection.py --fetch-data`

### 📊 Plotting: `plot_earthquakes.py`

**Purpose**: Create comprehensive earthquake analysis plots

**Key Functions**:
- `create_earthquake_plots()`: Generate individual plots
- `create_comprehensive_plot()`: Detailed analysis
- `create_comparison_plot()`: Cross-category comparison

**Called by**: `demo_detection.py --create-plots`

## Usage Examples

### Quick Start
```bash
# Run everything
python scripts/demo_detection.py --full-demo
```

### Step by Step
```bash
# 1. Fetch new data
python scripts/demo_detection.py --fetch-data

# 2. Test detection
python scripts/demo_detection.py --test-all-files

# 3. Create plots
python scripts/demo_detection.py --create-plots

# 4. Test synthetic data
python scripts/demo_detection.py --test-synthetic
```

### Individual Script Usage
```bash
# Direct script usage (not recommended)
python scripts/fetch_earthquake_data.py
python scripts/plot_earthquakes.py
```

## Script Dependencies

```
demo_detection.py
├── fetch_earthquake_data.py (imports functions)
├── plot_earthquakes.py (imports functions)
└── src/ (imports detection modules)
    ├── earthquake_detector.py
    ├── config.py
    └── utils.py
```

## Best Practices

1. **Use demo_detection.py as entry point** - Don't run other scripts directly
2. **Use --full-demo for complete workflow** - Ensures proper order
3. **Check logs for detailed output** - All scripts provide comprehensive logging
4. **Use --log-level for debugging** - Set to DEBUG for detailed output

## File Organization

```
scripts/
├── demo_detection.py          # Main entry point
├── fetch_earthquake_data.py   # USGS data fetching
├── plot_earthquakes.py        # Analysis plotting
└── README.md                  # This file
```

## Error Handling

All scripts include proper error handling:
- Import errors (missing dependencies)
- API errors (USGS connectivity)
- File errors (missing data files)
- Processing errors (detection failures)

Errors are logged with appropriate messages and the demo continues gracefully. 