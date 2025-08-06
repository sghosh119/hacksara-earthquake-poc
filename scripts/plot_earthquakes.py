#!/usr/bin/env python3
"""
Plot earthquake data for all 3 categories (big, borderline, small).
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import glob

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import load_sample_data

def create_earthquake_plots():
    """Create comprehensive plots for all earthquake categories."""
    print("🌍 Creating Earthquake Analysis Plots")
    print("=" * 50)
    
    # Find all earthquake data files
    earthquake_files = {
        'big': glob.glob("data/big_M*.csv"),
        'borderline': glob.glob("data/borderline_M*.csv"),
        'small': glob.glob("data/small_M*.csv")
    }
    
    print(f"📊 Found earthquake data files:")
    for category, files in earthquake_files.items():
        print(f"   - {category.upper()}: {len(files)} files")
    
    # Create plots for each category
    for category in ['big', 'borderline', 'small']:
        if not earthquake_files[category]:
            print(f"\n⚠️ No {category} earthquake files found")
            continue
            
        print(f"\n📈 Creating plots for {category.upper()} earthquakes...")
        
        for i, data_file in enumerate(earthquake_files[category][:2]):  # Plot up to 2 from each category
            print(f"   📊 Processing: {os.path.basename(data_file)}")
            
            # Load data
            data_info = load_sample_data(data_file)
            if data_info is None:
                print(f"   ❌ Failed to load {data_file}")
                continue
                
            data = data_info['data']
            
            # Load metadata
            metadata_file = data_file.replace('.csv', '_metadata.json')
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                actual_magnitude = metadata['earthquake_info']['magnitude']
                location = metadata['earthquake_info']['place']
                print(f"   📍 M{actual_magnitude} - {location}")
            except Exception as e:
                print(f"   ⚠️ Could not load metadata: {e}")
                actual_magnitude = 0
                location = "Unknown"
            
            # Create comprehensive plots
            create_comprehensive_plot(data, category, actual_magnitude, location, i+1)
    
    print(f"\n🎉 All earthquake plots created!")
    print(f"📁 Check the 'data/plots/' directory for generated plots")

def create_comprehensive_plot(data, category, magnitude, location, test_num):
    """Create comprehensive plots for earthquake analysis."""
    # Extract accelerometer data
    accel_x = data['accel_x'].values
    accel_y = data['accel_y'].values
    accel_z = data['accel_z'].values
    
    # Calculate acceleration magnitude
    accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    
    # Time axis
    time_axis = np.arange(len(accel_x)) / 104  # 104 Hz sample rate
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle(f'{category.upper()} Earthquake Analysis - M{magnitude} - {location}', fontsize=16, fontweight='bold')
    
    # Plot 1: Raw Accelerometer Data
    ax1 = axes[0, 0]
    ax1.plot(time_axis, accel_x, label='X-axis', alpha=0.8, linewidth=1)
    ax1.plot(time_axis, accel_y, label='Y-axis', alpha=0.8, linewidth=1)
    ax1.plot(time_axis, accel_z, label='Z-axis', alpha=0.8, linewidth=1)
    ax1.set_title('Raw Accelerometer Data', fontweight='bold')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Acceleration (g)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Acceleration Magnitude
    ax2 = axes[0, 1]
    ax2.plot(time_axis, accel_magnitude, color='red', linewidth=2, alpha=0.8)
    ax2.axhline(y=0.02, color='orange', linestyle='--', label='Initial Threshold (0.02g)', alpha=0.7)
    ax2.axhline(y=0.05, color='red', linestyle='--', label='Strong Threshold (0.05g)', alpha=0.7)
    ax2.axhline(y=0.08, color='purple', linestyle='--', label='M5.1+ Threshold (0.08g)', alpha=0.7)
    ax2.set_title('Acceleration Magnitude', fontweight='bold')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Acceleration Magnitude (g)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: STA/LTA Ratio
    ax3 = axes[1, 0]
    sta_window = 104  # 1 second
    lta_window = min(1040, len(accel_magnitude))  # 10 seconds
    
    if len(accel_magnitude) >= lta_window:
        sta = np.convolve(np.abs(accel_magnitude), np.ones(sta_window)/sta_window, mode='same')
        lta = np.convolve(np.abs(accel_magnitude), np.ones(lta_window)/lta_window, mode='same')
        lta = np.where(lta < 1e-10, 1e-10, lta)
        sta_lta_ratio = sta / lta
        
        ax3.plot(time_axis, sta_lta_ratio, color='green', linewidth=2, alpha=0.8)
        ax3.axhline(y=2.5, color='orange', linestyle='--', label='STA/LTA Threshold (2.5)', alpha=0.7)
        ax3.axhline(y=3.5, color='red', linestyle='--', label='Strong STA/LTA (3.5)', alpha=0.7)
        ax3.set_title('STA/LTA Ratio', fontweight='bold')
        ax3.set_xlabel('Time (seconds)')
        ax3.set_ylabel('STA/LTA Ratio')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Insufficient Data for STA/LTA', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('STA/LTA Ratio', fontweight='bold')
    
    # Plot 4: Frequency Domain Analysis
    ax4 = axes[1, 1]
    # Calculate FFT for frequency analysis
    fft_x = np.fft.fft(accel_x)
    fft_y = np.fft.fft(accel_y)
    fft_z = np.fft.fft(accel_z)
    
    freqs = np.fft.fftfreq(len(accel_x), 1/104)  # 104 Hz sample rate
    positive_freqs = freqs[:len(freqs)//2]
    
    # Plot power spectral density
    psd_x = np.abs(fft_x[:len(fft_x)//2])**2
    psd_y = np.abs(fft_y[:len(fft_y)//2])**2
    psd_z = np.abs(fft_z[:len(fft_z)//2])**2
    
    ax4.semilogy(positive_freqs, psd_x, label='X-axis', alpha=0.8)
    ax4.semilogy(positive_freqs, psd_y, label='Y-axis', alpha=0.8)
    ax4.semilogy(positive_freqs, psd_z, label='Z-axis', alpha=0.8)
    ax4.axvline(x=0.5, color='orange', linestyle='--', label='Low Cut (0.5 Hz)', alpha=0.7)
    ax4.axvline(x=5.0, color='red', linestyle='--', label='High Cut (5.0 Hz)', alpha=0.7)
    ax4.set_title('Frequency Domain Analysis', fontweight='bold')
    ax4.set_xlabel('Frequency (Hz)')
    ax4.set_ylabel('Power Spectral Density')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 20)  # Focus on seismic frequencies
    
    # Plot 5: Detection Metrics
    ax5 = axes[2, 0]
    
    # Calculate detection metrics
    pga = np.max(accel_magnitude)
    normalized_pga = pga / 10.0  # Normalize for comparison
    
    metrics = ['PGA', 'Normalized PGA', 'Max STA/LTA', 'Duration']
    values = [pga, normalized_pga, np.max(sta_lta_ratio) if len(accel_magnitude) >= lta_window else 1.0, 
              np.sum(accel_magnitude > 0.02) / 104]
    
    colors = ['red' if val > 0.08 else 'orange' if val > 0.05 else 'blue' for val in values]
    
    bars = ax5.bar(metrics, values, color=colors, alpha=0.7)
    ax5.set_title('Detection Metrics', fontweight='bold')
    ax5.set_ylabel('Value')
    ax5.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}', ha='center', va='bottom')
    
    # Plot 6: Summary Statistics
    ax6 = axes[2, 1]
    ax6.axis('off')
    
    # Calculate statistics
    max_pga = np.max(accel_magnitude)
    min_pga = np.min(accel_magnitude)
    mean_pga = np.mean(accel_magnitude)
    std_pga = np.std(accel_magnitude)
    
    # Detection criteria
    threshold_initial = 0.02
    threshold_strong = 0.05
    threshold_m51 = 0.08
    
    pga_check = max_pga > threshold_initial
    strong_check = max_pga > threshold_strong
    m51_check = normalized_pga > threshold_m51
    
    summary_text = f"""
Earthquake Analysis Summary
==========================

Magnitude: M{magnitude}
Category: {category.upper()}
Location: {location}

PGA Statistics:
- Maximum PGA: {max_pga:.4f}g
- Minimum PGA: {min_pga:.4f}g
- Mean PGA: {mean_pga:.4f}g
- Std Dev PGA: {std_pga:.4f}g

Detection Criteria:
- Initial Threshold (0.02g): {'✅ PASS' if pga_check else '❌ FAIL'}
- Strong Threshold (0.05g): {'✅ PASS' if strong_check else '❌ FAIL'}
- M5.1+ Threshold (0.08g): {'✅ PASS' if m51_check else '❌ FAIL'}

Expected Detection: {'YES' if magnitude >= 5.1 else 'NO'}
"""
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    # Save the plot
    os.makedirs("data/plots", exist_ok=True)
    filename = f"{category}_M{magnitude}_test{test_num}_analysis.png"
    filepath = os.path.join("data/plots", filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {filename}")

def create_comparison_plot():
    """Create a comparison plot showing all earthquake categories together."""
    print(f"\n📊 Creating comparison plot...")
    
    # Load one example from each category
    categories = ['big', 'borderline', 'small']
    data_samples = {}
    
    for category in categories:
        files = glob.glob(f"data/{category}_M*.csv")
        if files:
            data_info = load_sample_data(files[0])
            if data_info:
                data_samples[category] = data_info['data']
                
                # Load metadata
                metadata_file = files[0].replace('.csv', '_metadata.json')
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    data_samples[f"{category}_magnitude"] = metadata['earthquake_info']['magnitude']
                    data_samples[f"{category}_location"] = metadata['earthquake_info']['place']
                except:
                    data_samples[f"{category}_magnitude"] = 0
                    data_samples[f"{category}_location"] = "Unknown"
    
    if len(data_samples) < 3:
        print("   ⚠️ Not enough data for comparison plot")
        return
    
    # Create comparison plot
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    fig.suptitle('Earthquake Comparison: Big vs Borderline vs Small', fontsize=16, fontweight='bold')
    
    for i, category in enumerate(categories):
        if f"{category}_magnitude" not in data_samples:
            continue
            
        data = data_samples[category]
        magnitude = data_samples[f"{category}_magnitude"]
        location = data_samples[f"{category}_location"]
        
        # Extract accelerometer data
        accel_x = data['accel_x'].values
        accel_y = data['accel_y'].values
        accel_z = data['accel_z'].values
        accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        
        # Time axis
        time_axis = np.arange(len(accel_x)) / 104
        
        # Plot
        ax = axes[i]
        ax.plot(time_axis, accel_magnitude, linewidth=2, alpha=0.8, 
                label=f'M{magnitude} - {location}')
        ax.axhline(y=0.02, color='orange', linestyle='--', alpha=0.7, label='Initial Threshold')
        ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='Strong Threshold')
        ax.axhline(y=0.08, color='purple', linestyle='--', alpha=0.7, label='M5.1+ Threshold')
        
        ax.set_title(f'{category.upper()} Earthquake (M{magnitude})', fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Acceleration Magnitude (g)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Save comparison plot
    os.makedirs("data/plots", exist_ok=True)
    filepath = os.path.join("data/plots", "earthquake_comparison.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: earthquake_comparison.png")

def main():
    """Main function to create earthquake plots."""
    print("🌍 Earthquake Data Visualization")
    print("=" * 50)
    
    # Create individual plots for each category
    create_earthquake_plots()
    
    # Create comparison plot
    create_comparison_plot()
    
    print(f"\n🎉 All plots created successfully!")
    print(f"📁 Check 'data/plots/' directory for generated visualizations")

if __name__ == "__main__":
    main() 