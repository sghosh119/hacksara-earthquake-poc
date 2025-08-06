"""
Configuration settings for the earthquake detection system.
"""

import os
from typing import Optional


class Settings:
    """Configuration settings for earthquake detection."""
    
    def __init__(self):
        # Detection Parameters
        self.pga_threshold = float(os.getenv("EARTHQUAKE_PGA_THRESHOLD", "0.02"))
        self.pga_confirmation = float(os.getenv("EARTHQUAKE_PGA_CONFIRMATION", "0.05"))
        self.sta_lta_threshold = float(os.getenv("EARTHQUAKE_STA_LTA_THRESHOLD", "2.5"))
        self.min_duration_seconds = float(os.getenv("EARTHQUAKE_MIN_DURATION_SECONDS", "0.5"))
        
        # Filtering Parameters
        self.low_cut_freq = float(os.getenv("EARTHQUAKE_LOW_CUT_FREQ", "0.5"))
        self.high_cut_freq = float(os.getenv("EARTHQUAKE_HIGH_CUT_FREQ", "5.0"))
        self.filter_order = int(os.getenv("EARTHQUAKE_FILTER_ORDER", "4"))
        
        # Processing Parameters
        self.sta_window_seconds = float(os.getenv("EARTHQUAKE_STA_WINDOW_SECONDS", "1.0"))
        self.lta_window_seconds = float(os.getenv("EARTHQUAKE_LTA_WINDOW_SECONDS", "10.0"))
        self.sample_rate = int(os.getenv("EARTHQUAKE_SAMPLE_RATE", "104"))
        
        # Output Settings
        self.save_detection_plots = os.getenv("EARTHQUAKE_SAVE_DETECTION_PLOTS", "True").lower() == "true"
        
        # Logging
        self.log_level = os.getenv("EARTHQUAKE_LOG_LEVEL", "INFO")
        

    
 