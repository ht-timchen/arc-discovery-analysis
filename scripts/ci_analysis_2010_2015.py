#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P

def count_chief_investigators(ci_string):
    """Count the number of chief investigators from a semicolon-separated string"""
    if not ci_string or ci_string.strip() == '':
        return 0
    # Split by semicolon and count non-empty entries
    investigators = [ci.strip() for ci in ci_string.split(';') if ci.strip()]
    return len(investigators)

def analyze_ci_data():
    """Analyze the Chief Investigator data from 2010-2025"""
    
    # Data storage
    yearly_ci_counts = defaultdict(list)  # year -> list of CI counts for each project
    
    print("Loading and analyzing Discovery Projects data...")
    
    with open(P.DISCOVERY_CSV_2026, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                year = int(row['funding_commencement_year'])
                
                # Filter for 2010-2025
                if 2010 <= year <= 2025:
                    ci_count = count_chief_investigators(row['chief_investigators'])
                    yearly_ci_counts[year].append(ci_count)
                    
            except (ValueError, TypeError):
                # Skip rows with invalid years
                continue
    
    # Calculate average CI counts per year
    yearly_averages = {}
    yearly_totals = {}
    yearly_project_counts = {}
    
    for year in range(2010, 2026):
        if year in yearly_ci_counts:
            ci_counts = yearly_ci_counts[year]
            yearly_averages[year] = np.mean(ci_counts)
            yearly_totals[year] = sum(ci_counts)
            yearly_project_counts[year] = len(ci_counts)
        else:
            yearly_averages[year] = 0
            yearly_totals[year] = 0
            yearly_project_counts[year] = 0
    
    return yearly_averages, yearly_totals, yearly_project_counts, yearly_ci_counts

def create_visualization():
    """Create the visualization of average CI counts"""
    
    yearly_averages, yearly_totals, yearly_project_counts, yearly_ci_counts = analyze_ci_data()
    
    # Print summary statistics
    print("\nSummary Statistics (2010-2025):")
    print("=" * 50)
    for year in range(2010, 2026):
        avg_ci = yearly_averages[year]
        total_projects = yearly_project_counts[year]
        total_cis = yearly_totals[year]
        if total_projects > 0:  # Only print years with data
            print(f"{year}: {total_projects:3d} projects, {total_cis:4d} total CIs, {avg_ci:.2f} avg CIs/project")
    
    # Create the plot
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Only include years with data for plotting
    years = [year for year in range(2010, 2026) if yearly_project_counts[year] > 0]
    averages = [yearly_averages[year] for year in years]
    project_counts = [yearly_project_counts[year] for year in years]
    
    # Plot 1: Average CI per project
    bars1 = ax1.bar(years, averages, color='steelblue', alpha=0.8, edgecolor='navy')
    ax1.set_title('Average Number of Chief Investigators per Discovery Project (2010-2025)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Funding Commencement Year', fontsize=12)
    ax1.set_ylabel('Average Number of Chief Investigators', fontsize=12)
    ax1.set_ylim(0, max(averages) * 1.1)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, avg in zip(bars1, averages):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{avg:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Number of projects per year
    bars2 = ax2.bar(years, project_counts, color='lightcoral', alpha=0.8, edgecolor='darkred')
    ax2.set_title('Number of Discovery Projects per Year (2010-2025)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlabel('Funding Commencement Year', fontsize=12)
    ax2.set_ylabel('Number of Projects', fontsize=12)
    ax2.set_ylim(0, max(project_counts) * 1.1)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, count in zip(bars2, project_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    P.OUTPUTS_ANALYSIS.mkdir(parents=True, exist_ok=True)
    plt.savefig(P.OUTPUTS_ANALYSIS / 'ci_analysis_2010_2025.png', dpi=300, bbox_inches='tight')
    plt.savefig(P.OUTPUTS_ANALYSIS / 'ci_analysis_2010_2025.pdf', bbox_inches='tight')
    print(f"\nPlot saved under {P.OUTPUTS_ANALYSIS}: ci_analysis_2010_2025.png and .pdf")
    
    # Create distribution analysis - show key years only for readability
    # Select representative years across the time period
    key_years = [2010, 2012, 2015, 2018, 2021, 2024, 2025]
    available_years = [year for year in key_years if year in yearly_ci_counts and yearly_ci_counts[year]]
    
    if available_years:
        n_years = len(available_years)
        cols = 3
        rows = (n_years + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        if rows == 1:
            axes = axes.reshape(1, -1)
        fig.suptitle('Distribution of Chief Investigators per Project by Key Years (2010-2025)', 
                     fontsize=16, fontweight='bold')
        
        for i, year in enumerate(available_years):
            row = i // cols
            col = i % cols
            ax = axes[row, col]
            
            ci_counts = yearly_ci_counts[year]
            bins = range(1, max(ci_counts) + 2)
            ax.hist(ci_counts, bins=bins, alpha=0.7, color='steelblue', edgecolor='navy')
            ax.set_title(f'{year}\n(n={len(ci_counts)} projects)', fontweight='bold')
            ax.set_xlabel('Number of Chief Investigators')
            ax.set_ylabel('Number of Projects')
            ax.grid(True, alpha=0.3)
            
            # Add mean line
            mean_ci = np.mean(ci_counts)
            ax.axvline(mean_ci, color='red', linestyle='--', linewidth=2, 
                      label=f'Mean: {mean_ci:.2f}')
            ax.legend()
        
        # Hide unused subplots
        for i in range(len(available_years), rows * cols):
            row = i // cols
            col = i % cols
            axes[row, col].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(P.OUTPUTS_ANALYSIS / 'ci_distribution_2010_2025.png', dpi=300, bbox_inches='tight')
        plt.savefig(P.OUTPUTS_ANALYSIS / 'ci_distribution_2010_2025.pdf', bbox_inches='tight')
        print(f"Distribution plot saved under {P.OUTPUTS_ANALYSIS}: ci_distribution_2010_2025.png and .pdf")
    
    plt.show()

if __name__ == "__main__":
    create_visualization()
