#!/usr/bin/env python3
"""Data processing module for charitable donation analysis.

Handles CSV reading, data cleaning, and type conversion.
"""

import pandas as pd
import re
from fidchar.core import analysis as ca
from fidchar.core import visualization as viz

def parse_amount(amount_str):
    """Convert amount string like '$1,000.00' to float"""
    if pd.isna(amount_str) or amount_str == "":
        return 0.0
    # Remove dollar sign, commas, and convert to float
    cleaned = re.sub(r"[$,]", "", str(amount_str))
    return float(cleaned)


def read_donation_data(file_path):
    """Read and parse the CSV donation data"""
    try:
        df = pd.read_csv(file_path, skiprows=8)
    except FileNotFoundError:
        raise FileNotFoundError(f"data.csv file not found at {file_path}")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert amount column to numeric
    df["Amount_Numeric"] = df["Amount"].apply(parse_amount)

    # Convert dates to datetime
    df["Submit Date"] = pd.to_datetime(df["Submit Date"])
    df["Year"] = df["Submit Date"].dt.year

    return df

def analyze_top_charities(df, top_n):
    """Orchestrate top charities analysis.

    Note: Charity descriptions now come from charapi evaluations, not separate API calls.
    """
    # Get basic top charities data
    top_charities = ca.get_top_charities_basic(df, top_n)

    # Get detailed donation history for each top charity
    charity_details = ca.get_charity_details(df, top_charities)

    # Create yearly graphs for each charity (only if they have recent donations)
    graph_info = viz.create_charity_yearly_graphs(top_charities, charity_details)

    return top_charities, charity_details, graph_info
