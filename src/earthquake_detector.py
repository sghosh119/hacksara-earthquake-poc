"""
Earthquake detection system using IMU data.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

from config import Settings
from filters import apply_bandpass_filter
from utils import save_detection_plot

logger = logging.getLogger(__name__)


class EarthquakeDetector:
    """Earthquake detection system using IMU accelerometer data."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the earthquake detector.
        
        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()
        self.logger = logging.getLogger(__name__)
        
        # Initialize detection state
        self.detection_count = 0
        self.last_detection_time = None
        
        self.logger.info("Earthquake detector initialized")
    
    def process_imu_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Process IMU data and detect earthquakes.
        
        Args:
            data: DataFrame containing IMU data with columns:
                  accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
                  
        Returns:
            Dictionary containing detection results and processed data
        """
        try:
            # Extract accelerometer data
            accel_x = data['accel_x'].values
            accel_y = data['accel_y'].values
            accel_z = data['accel_z'].values
            
            # Apply bandpass filter
            filtered_accel_x = apply_bandpass_filter(
                accel_x, 
                self.settings.sample_rate,
                self.settings.low_cut_freq,
                self.settings.high_cut_freq,
                self.settings.filter_order
            )
            filtered_accel_y = apply_bandpass_filter(
                accel_y, 
                self.settings.sample_rate,
                self.settings.low_cut_freq,
                self.settings.high_cut_freq,
                self.settings.filter_order
            )
            filtered_accel_z = apply_bandpass_filter(
                accel_z, 
                self.settings.sample_rate,
                self.settings.low_cut_freq,
                self.settings.high_cut_freq,
                self.settings.filter_order
            )
            
            # Calculate STA/LTA ratios
            sta_window = int(self.settings.sta_window_seconds * self.settings.sample_rate)
            lta_window = int(self.settings.lta_window_seconds * self.settings.sample_rate)
            
            sta_lta_x = self._calculate_sta_lta(filtered_accel_x, sta_window, lta_window)
            sta_lta_y = self._calculate_sta_lta(filtered_accel_y, sta_window, lta_window)
            sta_lta_z = self._calculate_sta_lta(filtered_accel_z, sta_window, lta_window)
            
            # Calculate PGA values
            pga_x = np.max(np.abs(filtered_accel_x))
            pga_y = np.max(np.abs(filtered_accel_y))
            pga_z = np.max(np.abs(filtered_accel_z))
            pga_magnitude = np.sqrt(pga_x**2 + pga_y**2 + pga_z**2)
            
            # Calculate maximum STA/LTA ratio
            max_sta_lta = max(np.max(sta_lta_x), np.max(sta_lta_y), np.max(sta_lta_z))
            
            # Check duration criteria
            duration_check = self._check_duration_criteria(filtered_accel_x, filtered_accel_y, filtered_accel_z)
            
            # Perform detection
            detection_result = self._perform_detection(
                pga_x, pga_y, pga_z, pga_magnitude,
                max_sta_lta, duration_check
            )
            
            # Prepare processed data
            processed_data = {
                'filtered_accel_x': filtered_accel_x,
                'filtered_accel_y': filtered_accel_y,
                'filtered_accel_z': filtered_accel_z,
                'sta_lta_x': sta_lta_x,
                'sta_lta_y': sta_lta_y,
                'sta_lta_z': sta_lta_z
            }
            
            
            
            # Handle detection
            if detection_result['detected']:
                self._handle_detection(processed_data, detection_result)
            
            return {
                'processed_data': processed_data,
                'detection_result': detection_result
            }
            
        except Exception as e:
            self.logger.error(f"Error processing IMU data: {e}")
            return {
                'processed_data': {},
                'detection_result': {
                    'detected': False,
                    'error': str(e)
                }
            }
    
    def _calculate_sta_lta(self, data: np.ndarray, sta_window: int, lta_window: int) -> np.ndarray:
        """
        Calculate STA/LTA ratio for earthquake detection.
        
        Args:
            data: Input signal data
            sta_window: Short-term average window size
            lta_window: Long-term average window size
            
        Returns:
            STA/LTA ratio array
        """
        # Calculate short-term average
        sta = np.convolve(np.abs(data), np.ones(sta_window)/sta_window, mode='same')
        
        # Calculate long-term average
        lta = np.convolve(np.abs(data), np.ones(lta_window)/lta_window, mode='same')
        
        # Avoid division by zero
        lta = np.where(lta < 1e-10, 1e-10, lta)
        
        return sta / lta
    
    def _check_duration_criteria(self, accel_x: np.ndarray, accel_y: np.ndarray, accel_z: np.ndarray) -> bool:
        """
        Check if the signal duration meets the minimum requirement.
        
        Args:
            accel_x: X-axis accelerometer data
            accel_y: Y-axis accelerometer data
            accel_z: Z-axis accelerometer data
            
        Returns:
            True if duration criteria is met
        """
        # Calculate acceleration magnitude
        accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        
        # Count samples above threshold
        threshold_samples = np.sum(accel_magnitude > self.settings.pga_threshold)
        
        # Convert to duration
        duration_seconds = threshold_samples / self.settings.sample_rate
        
        return duration_seconds >= self.settings.min_duration_seconds
    
    def _perform_detection(self, pga_x: float, pga_y: float, pga_z: float, 
                          pga_magnitude: float, max_sta_lta: float, duration_check: bool) -> Dict[str, Any]:
        """
        Perform earthquake detection based on multiple criteria.
        
        Args:
            pga_x: Peak ground acceleration X-axis
            pga_y: Peak ground acceleration Y-axis
            pga_z: Peak ground acceleration Z-axis
            pga_magnitude: Combined PGA magnitude
            max_sta_lta: Maximum STA/LTA ratio
            duration_check: Duration criteria result
            
        Returns:
            Detection result dictionary
        """
        # Check individual criteria
        pga_criteria = pga_magnitude > self.settings.pga_threshold
        sta_lta_criteria = max_sta_lta > self.settings.sta_lta_threshold
        duration_criteria = duration_check
        
        # Determine detection
        detected = pga_criteria and sta_lta_criteria and duration_criteria
        
        # Calculate confidence score (0-4)
        confidence_score = sum([pga_criteria, sta_lta_criteria, duration_criteria])
        
        # Determine severity
        if pga_magnitude > self.settings.pga_confirmation:
            severity = "HIGH"
        elif detected:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        # Prepare result
        result = {
            'detected': detected,
            'severity': severity,
            'confidence_score': confidence_score,
            'timestamp': datetime.now().isoformat(),
            'criteria': {
                'pga_threshold': pga_criteria,
                'sta_lta_threshold': sta_lta_criteria,
                'duration_check': duration_criteria
            },
            'metrics': {
                'pga_x': pga_x,
                'pga_y': pga_y,
                'pga_z': pga_z,
                'pga_magnitude': pga_magnitude,
                'max_sta_lta': max_sta_lta,
                'duration_check': duration_check
            },
            'thresholds': {
                'pga_threshold': self.settings.pga_threshold,
                'pga_confirmation': self.settings.pga_confirmation,
                'sta_lta_threshold': self.settings.sta_lta_threshold,
                'min_duration_seconds': self.settings.min_duration_seconds
            }
        }
        
        return result
    
    def _handle_detection(self, processed_data: Dict[str, Any], detection_result: Dict[str, Any]) -> None:
        """
        Handle earthquake detection event.
        
        Args:
            processed_data: Processed IMU data
            detection_result: Detection result
        """
        try:
            self.detection_count += 1
            self.last_detection_time = datetime.now()
            
            self.logger.warning(f"EARTHQUAKE DETECTED! Severity: {detection_result['severity']}, "
                              f"Confidence: {detection_result['confidence_score']}/4.0")
            
            # Save detection plot if enabled
            if self.settings.save_detection_plots:
                plot_filename = f"detection_{self.detection_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                save_detection_plot(processed_data, detection_result, plot_filename)
            
            self.logger.info(f"Detection #{self.detection_count} handled successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to handle detection: {e}")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """
        Get detection statistics.
        
        Returns:
            Dictionary containing detection statistics
        """
        return {
            'total_detections': self.detection_count,
            'last_detection_time': self.last_detection_time.isoformat() if self.last_detection_time else None,
            'settings': {
                'pga_threshold': self.settings.pga_threshold,
                'pga_confirmation': self.settings.pga_confirmation,
                'sta_lta_threshold': self.settings.sta_lta_threshold,
                'min_duration_seconds': self.settings.min_duration_seconds
            }
        } 