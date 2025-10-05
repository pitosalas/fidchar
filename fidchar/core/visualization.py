#!/usr/bin/env python3
"""Visualization module for charitable donation analysis.

Handles all matplotlib/seaborn chart generation with Tufte-style formatting.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set seaborn style for Tufte-inspired minimalist charts
sns.set_style("white")
sns.set_context("notebook", rc={"axes.linewidth": 0.5})
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.top"] = False


def create_yearly_histograms(yearly_amounts, yearly_counts):
    """Create Tufte-style minimalist histograms for yearly data"""
    # Create images directory if it doesn't exist
    os.makedirs("../output/images", exist_ok=True)

    # Create amount histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(yearly_amounts.index, yearly_amounts.values,
                  color="steelblue", alpha=0.7, width=0.6)

    # Tufte style: minimal text, remove chart junk
    ax.set_title("Donations by Year", fontsize=12, pad=15, fontweight="normal")
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Format y-axis as currency, remove grid
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:,.0f}K" if x >= 1000 else f"${x:,.0f}"))
    ax.tick_params(axis="both", which="major", labelsize=9)

    # Remove spines and ticks for Tufte style
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    plt.tight_layout()
    plt.savefig("../output/images/yearly_amounts.png", dpi=200, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()

    # Create count histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(yearly_counts.index, yearly_counts.values,
                  color="darkgreen", alpha=0.7, width=0.6)

    ax.set_title("Number of Donations by Year", fontsize=12, pad=15, fontweight="normal")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="both", which="major", labelsize=9)

    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    plt.tight_layout()
    plt.savefig("../output/images/yearly_counts.png", dpi=200, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()


def create_charity_yearly_graphs(top_charities, charity_details):
    """Create Tufte-style minimalist yearly donation graphs for each top charity"""
    created_graphs = {}

    for i, (tax_id, charity_data) in enumerate(top_charities.iterrows(), 1):
        org_name = charity_data["Organization"]
        donations = charity_details[tax_id].copy()

        # Group by year and sum donations
        donations["Year"] = donations["Submit Date"].dt.year
        yearly_totals = donations.groupby("Year")["Amount_Numeric"].sum()

        # Get all years from the data (full history)
        all_years = sorted(yearly_totals.index)
        if not all_years:
            created_graphs[tax_id] = None
            continue

        # Create complete year range from first to last donation year
        year_range = list(range(min(all_years), max(all_years) + 1))
        year_amounts = []
        for year in year_range:
            amount = yearly_totals.get(year, 0)
            year_amounts.append(amount)

        _create_single_charity_graph(i, tax_id, year_range, year_amounts, created_graphs)

    return created_graphs


def _create_single_charity_graph(i, tax_id, year_range, year_amounts, created_graphs):
    """Create individual charity graph (split for line length compliance)"""
    # Create very small, embedded thumbnail graph
    fig, ax = plt.subplots(figsize=(3, 1.5))  # Very compact for embedding

    # Use seaborn color palette
    color = sns.color_palette("husl", 10)[i-1] if i <= 10 else "steelblue"
    bars = ax.bar(year_range, year_amounts, color=color, alpha=0.8, width=0.7)

    # Ultra-minimal: no title for embedded thumbnail
    # Only show essential data

    # Remove labels and minimize text
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Smart y-axis formatting
    max_amount = max(year_amounts) if year_amounts else 0
    if max_amount >= 10000:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:,.0f}K" if x > 0 else ""))
    else:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}" if x > 0 else ""))

    # Ultra-minimal tick marks for thumbnail
    ax.tick_params(axis="both", which="major", labelsize=6)
    ax.tick_params(axis="x", rotation=0)

    # Show only first, middle, and last year for compact display
    num_years = len(year_range)
    if num_years >= 3:
        years_to_show = [year_range[0], year_range[num_years//2], year_range[-1]]
    else:
        years_to_show = year_range
    ax.set_xticks(years_to_show)

    # Remove all spines except bottom (Tufte style)
    sns.despine(left=True, right=True, top=True)
    ax.tick_params(left=False, right=False, top=False)

    # No grid (Tufte principle: remove non-data ink)
    ax.grid(False)

    plt.tight_layout()

    # Save very compact thumbnail
    filename = f"../output/images/charity_{i:02d}_{tax_id.replace('-', '')}.png"
    plt.savefig(filename, dpi=100, bbox_inches="tight", pad_inches=0.05,
                facecolor="white", edgecolor="none")
    plt.close()
    created_graphs[tax_id] = filename