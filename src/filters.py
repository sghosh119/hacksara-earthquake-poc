"""
Signal processing filters for earthquake detection.
"""

import numpy as np
from scipy import signal
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def apply_bandpass_filter(data: np.ndarray, sample_rate: int, low_cut: float, high_cut: float, order: int = 4) -> np.ndarray:
    """
    Apply bandpass filter to isolate seismic frequencies.
    
    Args:
        data: Input signal data
        sample_rate: Sampling rate in Hz
        low_cut: Low frequency cutoff
        high_cut: High frequency cutoff
        order: Filter order
        
    Returns:
        Filtered signal data
    """
    try:
        nyquist = sample_rate / 2
        low = low_cut / nyquist
        high = high_cut / nyquist
        
        # Butterworth filter design
        b, a = signal.butter(order, [low, high], btype='band')
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    except Exception as e:
        logger.error(f"Error applying bandpass filter: {e}")
        return data


 