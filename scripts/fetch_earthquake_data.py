#!/usr/bin/env python3
"""
Fetch real earthquake data from USGS API and convert to IMU format for testing.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def fetch_usgs_earthquakes(start_time=None, end_time=None, min_magnitude=5.0, max_magnitude=10.0):
    """
    Fetch earthquake data from USGS API.
    
    Args:
        start_time: Start time (datetime object)
        end_time: End time (datetime object)
        min_magnitude: Minimum earthquake magnitude
        max_magnitude: Maximum earthquake magnitude
        
    Returns:
        List of earthquake events
    """
    if start_time is None:
        start_time = datetime.now() - timedelta(days=30)  # Last 30 days
    if end_time is None:
        end_time = datetime.now()
    
    # Format dates for USGS API
    start_str = start_time.strftime('%Y-%m-%d')
    end_str = end_time.strftime('%Y-%m-%d')
    
    # USGS API endpoint
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    params = {
        'format': 'geojson',
        'starttime': start_str,
        'endtime': end_str,
        'minmagnitude': min_magnitude,
        'maxmagnitude': max_magnitude,
        'orderby': 'time'
    }
    
    try:
        print(f"🌍 Fetching earthquake data from USGS API...")
        print(f"   Date range: {start_str} to {end_str}")
        print(f"   Magnitude range: {min_magnitude} to {max_magnitude}")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        earthquakes = []
        for feature in data.get('features', []):
            properties = feature['properties']
            geometry = feature['geometry']
            
            earthquake = {
                'id': properties.get('id'),
                'magnitude': properties.get('mag'),
                'place': properties.get('place'),
                'time': datetime.fromtimestamp(properties.get('time', 0) / 1000),
                'longitude': geometry['coordinates'][0],
                'latitude': geometry['coordinates'][1],
                'depth': geometry['coordinates'][2],
                'type': properties.get('type'),
                'alert': properties.get('alert'),
                'tsunami': properties.get('tsunami', 0),
                'felt': properties.get('felt'),
                'cdi': properties.get('cdi'),
                'mmi': properties.get('mmi'),
                'url': properties.get('url')
            }
            earthquakes.append(earthquake)
        
        print(f"✅ Found {len(earthquakes)} earthquakes")
        return earthquakes
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from USGS API: {e}")
        return []

def convert_earthquake_to_imu_data(earthquake, duration_seconds=10.0, sample_rate=104):
    """
    Convert earthquake data to synthetic IMU data.
    
    Args:
        earthquake: Earthquake event dictionary
        duration_seconds: Duration of the IMU data
        sample_rate: Sampling rate in Hz
        
    Returns:
        Dictionary containing IMU data
    """
    n_samples = int(duration_seconds * sample_rate)
    time_axis = np.linspace(0, duration_seconds, n_samples)
    
    # Extract earthquake parameters
    magnitude = earthquake['magnitude']
    depth = earthquake['depth']
    
    # Convert magnitude to PGA (Peak Ground Acceleration)
    # This is a simplified conversion - in reality, PGA depends on distance, geology, etc.
    # For M5.0-6.0 earthquakes, PGA typically ranges from 0.02g to 0.2g
    base_pga = 0.02 * (magnitude - 4.0)  # Rough approximation
    base_pga = max(0.01, min(0.2, base_pga))  # Clamp between 0.01g and 0.2g
    
    # Generate normal operation data (low noise)
    normal_accel_x = np.random.normal(0, 0.001, n_samples)
    normal_accel_y = np.random.normal(0, 0.001, n_samples)
    normal_accel_z = np.random.normal(1, 0.001, n_samples)  # Gravity
    
    normal_gyro_x = np.random.normal(0, 0.1, n_samples)
    normal_gyro_y = np.random.normal(0, 0.1, n_samples)
    normal_gyro_z = np.random.normal(0, 0.1, n_samples)
    
    # Add earthquake event at 5 seconds
    earthquake_start_sample = int(5.0 * sample_rate)
    earthquake_duration_samples = int(3.0 * sample_rate)  # 3 second earthquake
    
    # Generate earthquake signature based on magnitude
    t_earthquake = np.linspace(0, 3.0, earthquake_duration_samples)
    
    # Create more realistic earthquake signal based on magnitude
    if magnitude >= 6.0:
        # Strong earthquake - multiple frequency components
        earthquake_signal = base_pga * (
            0.6 * np.sin(2 * np.pi * 2 * t_earthquake) * np.exp(-t_earthquake/1.5) +
            0.3 * np.sin(2 * np.pi * 1 * t_earthquake) * np.exp(-t_earthquake/2.0) +
            0.1 * np.sin(2 * np.pi * 3 * t_earthquake) * np.exp(-t_earthquake/1.0)
        )
    else:
        # Moderate earthquake - simpler signal
        earthquake_signal = base_pga * np.sin(2 * np.pi * 2 * t_earthquake) * np.exp(-t_earthquake/2)
    
    # Add earthquake to accelerometer data
    normal_accel_x[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal
    normal_accel_y[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal * 0.8
    normal_accel_z[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal * 0.6
    
    # Create timestamps
    timestamps = [earthquake['time'] + timedelta(seconds=t) for t in time_axis]
    
    # Create DataFrame
    data = pd.DataFrame({
        'timestamp': timestamps,
        'accel_x': normal_accel_x,
        'accel_y': normal_accel_y,
        'accel_z': normal_accel_z,
        'gyro_x': normal_gyro_x,
        'gyro_y': normal_gyro_y,
        'gyro_z': normal_gyro_z,
        'object_id': '281474982487350',
        'org_id': '7002229'
    })
    
    return {
        'data': data,
        'metadata': {
            'earthquake_id': earthquake['id'],
            'magnitude': magnitude,
            'place': earthquake['place'],
            'time': earthquake['time'],
            'depth': depth,
            'pga_estimate': base_pga,
            'duration_seconds': duration_seconds,
            'sample_rate': sample_rate
        }
    }



def categorize_earthquakes(earthquakes):
    """
    Categorize earthquakes into big, borderline, and small.
    
    Args:
        earthquakes: List of earthquake dictionaries
        
    Returns:
        Dictionary with categorized earthquakes
    """
    big_earthquakes = [eq for eq in earthquakes if eq['magnitude'] >= 5.1]
    borderline_earthquakes = [eq for eq in earthquakes if 4.5 <= eq['magnitude'] < 5.1]
    small_earthquakes = [eq for eq in earthquakes if eq['magnitude'] < 4.5]
    
    return {
        'big': big_earthquakes,
        'borderline': borderline_earthquakes,
        'small': small_earthquakes
    }

def save_earthquake_data(earthquakes, category, base_dir="data"):
    """
    Save earthquake data to CSV files.
    
    Args:
        earthquakes: List of earthquake dictionaries
        category: Category name (big, borderline, small)
        base_dir: Base directory for saving files
    """
    if not earthquakes:
        print(f"⚠️  No {category} earthquakes found")
        return
    
    # Create directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    print(f"\n💾 Saving {category} earthquake data...")
    
    for i, earthquake in enumerate(earthquakes[:3]):  # Save top 3 from each category
        # Convert to IMU data
        imu_data = convert_earthquake_to_imu_data(earthquake)
        
        # Create filename
        magnitude = earthquake['magnitude']
        place = earthquake['place'].replace(' ', '_').replace(',', '').replace('km', 'km_')[:30]
        timestamp = earthquake['time'].strftime('%Y%m%d_%H%M')
        filename = f"{category}_M{magnitude}_{place}_{timestamp}.csv"
        filepath = os.path.join(base_dir, filename)
        
        # Save IMU data
        imu_data['data'].to_csv(filepath, index=False)
        
        # Save metadata
        metadata_file = filepath.replace('.csv', '_metadata.json')
        metadata = {
            'earthquake_info': {
                'id': earthquake.get('id'),
                'magnitude': earthquake['magnitude'],
                'place': earthquake['place'],
                'time': earthquake['time'].isoformat(),
                'depth': earthquake['depth'],
                'longitude': earthquake.get('longitude'),
                'latitude': earthquake.get('latitude')
            },
            'imu_data_info': {
                'duration_seconds': imu_data['metadata']['duration_seconds'],
                'sample_rate': imu_data['metadata']['sample_rate'],
                'estimated_pga': imu_data['metadata']['pga_estimate'],
                'total_samples': len(imu_data['data'])
            },
            'category': category,
            'detection_threshold': 5.1 if category == 'big' else 4.5 if category == 'borderline' else 4.0
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"   ✅ Saved: {filename}")
        print(f"      - Magnitude: M{magnitude}")
        print(f"      - Location: {earthquake['place']}")
        print(f"      - Time: {earthquake['time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"      - Estimated PGA: {imu_data['metadata']['pga_estimate']:.4f}g")

def main():
    """Main function to fetch and store earthquake data by category."""
    print("🌍 Earthquake Data Collection and Storage")
    print("=" * 60)
    
    # Fetch recent earthquakes
    earthquakes = fetch_usgs_earthquakes(
        start_time=datetime.now() - timedelta(days=30),  # Last 30 days for more variety
        min_magnitude=4.0,  # Include smaller earthquakes
        max_magnitude=7.0
    )
    
    if not earthquakes:
        print("❌ No earthquake data found.")
        return
    
    # Sort by magnitude (strongest first)
    earthquakes.sort(key=lambda x: x['magnitude'], reverse=True)
    
    print(f"\n📊 Found {len(earthquakes)} earthquakes:")
    for i, eq in enumerate(earthquakes[:10]):  # Show top 10
        print(f"   {i+1}. M{eq['magnitude']} - {eq['place']} ({eq['time'].strftime('%Y-%m-%d %H:%M')})")
    
    # Categorize earthquakes
    categories = categorize_earthquakes(earthquakes)
    
    print(f"\n📂 Categorizing earthquakes:")
    print(f"   - Big earthquakes (M≥5.1): {len(categories['big'])}")
    print(f"   - Borderline earthquakes (M4.5-5.0): {len(categories['borderline'])}")
    print(f"   - Small earthquakes (M<4.5): {len(categories['small'])}")
    
    # Save data for each category
    for category, eq_list in categories.items():
        save_earthquake_data(eq_list, category)
    
    # Create summary file
    summary_file = "data/earthquake_data_summary.json"
    summary = {
        'total_earthquakes': len(earthquakes),
        'categories': {
            'big': {
                'count': len(categories['big']),
                'magnitude_range': f"M{min([eq['magnitude'] for eq in categories['big']]) if categories['big'] else 0}-M{max([eq['magnitude'] for eq in categories['big']]) if categories['big'] else 0}",
                'examples': [{'magnitude': eq['magnitude'], 'place': eq['place'], 'time': eq['time'].isoformat()} for eq in categories['big'][:3]]
            },
            'borderline': {
                'count': len(categories['borderline']),
                'magnitude_range': f"M{min([eq['magnitude'] for eq in categories['borderline']]) if categories['borderline'] else 0}-M{max([eq['magnitude'] for eq in categories['borderline']]) if categories['borderline'] else 0}",
                'examples': [{'magnitude': eq['magnitude'], 'place': eq['place'], 'time': eq['time'].isoformat()} for eq in categories['borderline'][:3]]
            },
            'small': {
                'count': len(categories['small']),
                'magnitude_range': f"M{min([eq['magnitude'] for eq in categories['small']]) if categories['small'] else 0}-M{max([eq['magnitude'] for eq in categories['small']]) if categories['small'] else 0}",
                'examples': [{'magnitude': eq['magnitude'], 'place': eq['place'], 'time': eq['time'].isoformat()} for eq in categories['small'][:3]]
            }
        },
        'data_collection_time': datetime.now().isoformat(),
        'data_source': 'USGS API',
        'detection_thresholds': {
            'big_earthquake_threshold': 5.1,
            'borderline_earthquake_threshold': 4.5,
            'small_earthquake_threshold': 4.0
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📋 Summary saved to: {summary_file}")
    print(f"\n🎉 Data collection complete!")
    print(f"   - Total earthquakes processed: {len(earthquakes)}")
    print(f"   - Files saved to: data/ directory")
    print(f"   - Each category contains up to 3 representative earthquakes")

if __name__ == "__main__":
    main() 