#!/usr/bin/env python3
"""
Demo script for earthquake detection system.
Tests the detection system with sample data and real earthquake data.
"""

import sys
import os
import argparse
import logging
import pandas as pd
from datetime import datetime
import glob
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from earthquake_detector import EarthquakeDetector
from config import Settings
from utils import setup_logging, load_sample_data

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Earthquake Detection Demo")
    parser.add_argument('--data-file', type=str, default=None,
                       help='Path to specific data file to test')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--test-all-files', action='store_true',
                       help='Test all earthquake data files')
    parser.add_argument('--chunk-size', type=int, default=1000,
                       help='Chunk size for processing')
    parser.add_argument('--fetch-data', action='store_true',
                       help='Fetch new earthquake data from USGS API')
    parser.add_argument('--create-plots', action='store_true',
                       help='Create comprehensive earthquake analysis plots')
    parser.add_argument('--full-demo', action='store_true',
                       help='Run complete demo: fetch data, test detection, create plots')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Initialize settings
    settings = Settings()
    
    # Initialize detector
    detector = EarthquakeDetector(settings)
    
    logger.info("🌍 Earthquake Detection Demo")
    logger.info("=" * 50)
    
    # Full demo mode
    if args.full_demo:
        run_full_demo(detector, logger)
        return
    
    # Fetch new data
    if args.fetch_data:
        test_fetch_earthquake_data(logger)
    
    # Create plots
    if args.create_plots:
        test_create_earthquake_plots(logger)
    
    # Test with specific file
    if args.data_file:
        test_single_file(detector, args.data_file, logger)
    
    # Test all earthquake files
    elif args.test_all_files:
        test_all_earthquake_files(detector, logger)
    
    # Default: test with sample data
    else:
        test_sample_data(detector, logger)
    
    # Print final statistics
    stats = detector.get_detection_stats()
    logger.info(f"\n📊 Final Statistics:")
    logger.info(f"   Total Detections: {stats['total_detections']}")
    logger.info(f"   Last Detection: {stats['last_detection_time']}")
    
    logger.info("\n🎉 Demo completed!")

def run_full_demo(detector: EarthquakeDetector, logger: logging.Logger):
    """Run complete demo workflow."""
    logger.info("🚀 Running Complete Demo Workflow")
    logger.info("=" * 50)
    
    # Step 1: Fetch new earthquake data
    logger.info("\n📥 Step 1: Fetching earthquake data from USGS API...")
    test_fetch_earthquake_data(logger)
    
    # Step 2: Test detection with all files
    logger.info("\n🔍 Step 2: Testing earthquake detection...")
    test_all_earthquake_files(detector, logger)
    
    # Step 3: Create comprehensive plots
    logger.info("\n📊 Step 3: Creating analysis plots...")
    test_create_earthquake_plots(logger)
    
    logger.info("\n🎉 Full demo workflow completed!")

def test_fetch_earthquake_data(logger: logging.Logger):
    """Test fetching earthquake data from USGS API."""
    try:
        # Import fetch functionality
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from fetch_earthquake_data import fetch_usgs_earthquakes, categorize_earthquakes, save_earthquake_data
        
        logger.info("📥 Fetching earthquake data from USGS API...")
        
        # Fetch recent earthquakes
        earthquakes = fetch_usgs_earthquakes(
            start_time=datetime.now() - pd.Timedelta(days=30),
            min_magnitude=4.0,
            max_magnitude=7.0
        )
        
        if not earthquakes:
            logger.warning("⚠️ No earthquake data found.")
            return
        
        # Sort by magnitude (strongest first)
        earthquakes.sort(key=lambda x: x['magnitude'], reverse=True)
        
        logger.info(f"📊 Found {len(earthquakes)} earthquakes:")
        for i, eq in enumerate(earthquakes[:5]):  # Show top 5
            logger.info(f"   {i+1}. M{eq['magnitude']} - {eq['place']} ({eq['time'].strftime('%Y-%m-%d %H:%M')})")
        
        # Categorize earthquakes
        categories = categorize_earthquakes(earthquakes)
        
        logger.info(f"\n📂 Categorizing earthquakes:")
        logger.info(f"   - Big earthquakes (M≥5.1): {len(categories['big'])}")
        logger.info(f"   - Borderline earthquakes (M4.5-5.0): {len(categories['borderline'])}")
        logger.info(f"   - Small earthquakes (M<4.5): {len(categories['small'])}")
        
        # Save data for each category
        for category, eq_list in categories.items():
            save_earthquake_data(eq_list, category)
        
        logger.info("✅ Earthquake data fetching completed!")
        
    except ImportError as e:
        logger.error(f"❌ Error importing fetch_earthquake_data: {e}")
    except Exception as e:
        logger.error(f"❌ Error fetching earthquake data: {e}")

def test_create_earthquake_plots(logger: logging.Logger):
    """Test creating comprehensive earthquake plots."""
    try:
        # Import plot functionality
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from plot_earthquakes import create_earthquake_plots, create_comparison_plot
        
        logger.info("📊 Creating comprehensive earthquake plots...")
        
        # Create individual plots
        create_earthquake_plots()
        
        # Create comparison plot
        create_comparison_plot()
        
        logger.info("✅ Earthquake plots created successfully!")
        
    except ImportError as e:
        logger.error(f"❌ Error importing plot_earthquakes: {e}")
    except Exception as e:
        logger.error(f"❌ Error creating plots: {e}")

def test_single_file(detector: EarthquakeDetector, data_file: str, logger: logging.Logger):
    """Test detection with a specific data file."""
    logger.info(f"📊 Testing with file: {data_file}")
    
    # Load data
    data_info = load_sample_data(data_file)
    if data_info is None:
        logger.error(f"Failed to load data from {data_file}")
        return
    
    data = data_info['data']
    logger.info(f"   Loaded {len(data)} samples")
    
    # Process data
    result = detector.process_imu_data(data)
    
    # Display results
    display_detection_results(result, logger)

def test_all_earthquake_files(detector: EarthquakeDetector, logger: logging.Logger):
    """Test detection with all earthquake data files."""
    logger.info("📊 Testing with all earthquake data files")
    
    # Find all earthquake data files
    earthquake_files = {
        'big': glob.glob("data/big_M*.csv"),
        'borderline': glob.glob("data/borderline_M*.csv"),
        'small': glob.glob("data/small_M*.csv")
    }
    
    total_files = sum(len(files) for files in earthquake_files.values())
    logger.info(f"   Found {total_files} earthquake data files")
    
    detection_count = 0
    
    for category, files in earthquake_files.items():
        logger.info(f"\n📈 Testing {category.upper()} earthquakes ({len(files)} files)")
        
        for i, data_file in enumerate(files):
            logger.info(f"   📊 Processing: {os.path.basename(data_file)}")
            
            # Load data
            data_info = load_sample_data(data_file)
            if data_info is None:
                logger.error(f"   ❌ Failed to load {data_file}")
                continue
            
            data = data_info['data']
            
            # Process data
            result = detector.process_imu_data(data)
            
            # Check detection
            if result['detection_result']['detected']:
                detection_count += 1
                logger.info(f"   ✅ EARTHQUAKE DETECTED!")
            else:
                logger.info(f"   ⚪ No earthquake detected")
    
    logger.info(f"\n📊 Summary: {detection_count}/{total_files} files triggered detection")

def test_sample_data(detector: EarthquakeDetector, logger: logging.Logger):
    """Test detection with sample IMU data."""
    logger.info("📊 Testing with sample IMU data")
    
    # Load sample data
    data_info = load_sample_data()
    if data_info is None:
        logger.error("Sample data not found. Please ensure data/sample_imu_data.csv exists.")
        return
    
    data = data_info['data']
    logger.info(f"   Loaded {len(data)} samples from sample data")
    
    # Process data
    result = detector.process_imu_data(data)
    
    # Display results
    display_detection_results(result, logger)



def display_detection_results(result: Dict[str, Any], logger: logging.Logger):
    """Display detection results."""
    detection_result = result['detection_result']
    
    if detection_result['detected']:
        logger.warning("🚨 EARTHQUAKE DETECTED!")
        logger.info(f"   Severity: {detection_result['severity']}")
        logger.info(f"   Confidence: {detection_result['confidence_score']}/4.0")
        logger.info(f"   PGA Magnitude: {detection_result['metrics']['pga_magnitude']:.4f}g")
        logger.info(f"   Max STA/LTA: {detection_result['metrics']['max_sta_lta']:.2f}")
    else:
        logger.info("✅ No earthquake detected")
        if 'error' in detection_result:
            logger.error(f"   Error: {detection_result['error']}")

if __name__ == "__main__":
    main() 