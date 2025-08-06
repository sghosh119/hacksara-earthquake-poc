"""
Utility functions for the earthquake detection system.
"""

import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def save_detection_plot(processed_data: Dict[str, Any], detection_result: Dict[str, Any], 
                       filename: str, save_dir: str = "data/plots") -> bool:
    """
    Save a plot of the detection event.
    
    Args:
        processed_data: Processed IMU data
        detection_result: Detection result
        filename: Output filename
        save_dir: Directory to save plots
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create save directory
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        
        # Create figure with subplots
        fig, axes = plt.subplots(3, 2, figsize=(15, 10))
        fig.suptitle(f"Earthquake Detection Event - {detection_result['timestamp']}", fontsize=16)
        
        # Plot 1: Raw vs Filtered Accelerometer Data
        ax1 = axes[0, 0]
        time_axis = np.arange(len(processed_data['filtered_accel_x'])) / 104  # 104 Hz
        
        ax1.plot(time_axis, processed_data['filtered_accel_x'], label='X-axis', alpha=0.7)
        ax1.plot(time_axis, processed_data['filtered_accel_y'], label='Y-axis', alpha=0.7)
        ax1.plot(time_axis, processed_data['filtered_accel_z'], label='Z-axis', alpha=0.7)
        ax1.set_title('Filtered Accelerometer Data')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Acceleration (g)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: STA/LTA Ratios
        ax2 = axes[0, 1]
        ax2.plot(time_axis, processed_data['sta_lta_x'], label='X-axis', alpha=0.7)
        ax2.plot(time_axis, processed_data['sta_lta_y'], label='Y-axis', alpha=0.7)
        ax2.plot(time_axis, processed_data['sta_lta_z'], label='Z-axis', alpha=0.7)
        ax2.axhline(y=detection_result['thresholds']['sta_lta_threshold'], color='r', linestyle='--', label='Threshold')
        ax2.set_title('STA/LTA Ratios')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('STA/LTA Ratio')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: PGA Values
        ax3 = axes[1, 0]
        pga_values = [detection_result['metrics']['pga_x'], 
                     detection_result['metrics']['pga_y'], 
                     detection_result['metrics']['pga_z']]
        pga_labels = ['X-axis', 'Y-axis', 'Z-axis']
        colors = ['red' if pga > detection_result['thresholds']['pga_threshold'] else 'blue' for pga in pga_values]
        
        bars = ax3.bar(pga_labels, pga_values, color=colors, alpha=0.7)
        ax3.axhline(y=detection_result['thresholds']['pga_threshold'], color='orange', linestyle='--', label='Threshold')
        ax3.axhline(y=detection_result['thresholds']['pga_confirmation'], color='red', linestyle='--', label='Confirmation')
        ax3.set_title('Peak Ground Acceleration (PGA)')
        ax3.set_ylabel('PGA (g)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Detection Criteria
        ax4 = axes[1, 1]
        criteria = detection_result['criteria']
        criteria_names = list(criteria.keys())
        criteria_values = [1 if criteria[name] else 0 for name in criteria_names]
        colors = ['green' if val else 'red' for val in criteria_values]
        
        bars = ax4.bar(criteria_names, criteria_values, color=colors, alpha=0.7)
        ax4.set_title('Detection Criteria')
        ax4.set_ylabel('Passed (1) / Failed (0)')
        ax4.set_ylim(0, 1.2)
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Detection Summary
        ax5 = axes[2, 0]
        ax5.axis('off')
        
        # Create summary text
        summary_text = f"""
Detection Summary
================
Timestamp: {detection_result['timestamp']}
Detected: {'YES' if detection_result['detected'] else 'NO'}
Severity: {detection_result.get('severity', 'N/A')}
Confidence: {detection_result.get('confidence_score', 'N/A')}/4.0

PGA Values:
- X-axis: {detection_result['metrics']['pga_x']:.4f}g
- Y-axis: {detection_result['metrics']['pga_y']:.4f}g  
- Z-axis: {detection_result['metrics']['pga_z']:.4f}g
- Magnitude: {detection_result['metrics']['pga_magnitude']:.4f}g

Max STA/LTA: {detection_result['metrics']['max_sta_lta']:.2f}
"""
        
        ax5.text(0.05, 0.95, summary_text, transform=ax5.transAxes, fontsize=10,
                 verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
        

        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Detection plot saved: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save detection plot: {e}")
        return False


def load_sample_data(filepath: str = "data/sample_imu_data.csv") -> Optional[Dict[str, Any]]:
    """
    Load sample IMU data from CSV file.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        Dictionary containing the data and metadata
    """
    try:
        import pandas as pd
        
        if not os.path.exists(filepath):
            logger.warning(f"Sample data file not found: {filepath}")
            return None
            
        data = pd.read_csv(filepath)
        
        # Convert timestamp column if it exists
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        return {
            'data': data,
            'filepath': filepath,
            'shape': data.shape,
            'columns': list(data.columns)
        }
        
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        return None


def generate_synthetic_earthquake_data(duration_seconds: float = 10.0, 
                                     sample_rate: int = 104,
                                     earthquake_start: float = 5.0,
                                     earthquake_magnitude: float = 0.03) -> Dict[str, Any]:
    """
    Generate synthetic IMU data with an embedded earthquake event.
    
    Args:
        duration_seconds: Total duration of the data
        sample_rate: Sampling rate in Hz
        earthquake_start: When the earthquake starts (seconds)
        earthquake_magnitude: Magnitude of the earthquake signal
        
    Returns:
        Dictionary containing synthetic data
    """
    # Generate time axis
    n_samples = int(duration_seconds * sample_rate)
    time_axis = np.linspace(0, duration_seconds, n_samples)
    
        # Generate normal operation data (low noise)
    normal_accel_x = np.random.normal(0, 0.001, n_samples)
    normal_accel_y = np.random.normal(0, 0.001, n_samples)
    normal_accel_z = np.random.normal(1, 0.001, n_samples)  # Gravity
    
    # Add earthquake event
    earthquake_start_sample = int(earthquake_start * sample_rate)
    earthquake_duration_samples = int(3.0 * sample_rate)  # 3 second earthquake
    
    # Generate earthquake signature (0.5-5 Hz bandpass filtered)
    t_earthquake = np.linspace(0, 3.0, earthquake_duration_samples)
    earthquake_signal = earthquake_magnitude * np.sin(2 * np.pi * 2 * t_earthquake) * np.exp(-t_earthquake/2)
    
    # Add earthquake to accelerometer data
    normal_accel_x[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal
    normal_accel_y[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal * 0.8
    normal_accel_z[earthquake_start_sample:earthquake_start_sample+earthquake_duration_samples] += earthquake_signal * 0.6
    
    # Create DataFrame
    import pandas as pd
    from datetime import datetime, timedelta
    
    timestamps = [datetime.now() + timedelta(seconds=t) for t in time_axis]
    
    data = pd.DataFrame({
        'timestamp': timestamps,
        'accel_x': normal_accel_x,
        'accel_y': normal_accel_y,
        'accel_z': normal_accel_z,
        'object_id': '281474982487350',
        'org_id': '7002229'
    })
    
    return {
        'data': data,
        'metadata': {
            'duration_seconds': duration_seconds,
            'sample_rate': sample_rate,
            'earthquake_start': earthquake_start,
            'earthquake_magnitude': earthquake_magnitude,
            'earthquake_duration': 3.0
        }
    }


def setup_logging(log_level: str = "INFO", log_file: str = "logs/earthquake_detector.log") -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Log file path
    """
    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")


 