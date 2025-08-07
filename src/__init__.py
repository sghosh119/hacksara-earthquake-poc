"""
Earthquake detection system package.
"""

from .config import Settings
from .earthquake_detector import EarthquakeDetector
from .filters import apply_bandpass_filter
from .utils import save_detection_plot, load_sample_data, setup_logging

__version__ = "1.0.0"

__all__ = [
    'Settings',
    'EarthquakeDetector',
    'apply_bandpass_filter',
    'save_detection_plot',
    'load_sample_data',
    'setup_logging'
] 