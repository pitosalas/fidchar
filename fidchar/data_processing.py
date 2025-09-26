#!/usr/bin/env python3
"""Data processing module for charitable donation analysis.

Handles CSV reading, data cleaning, and type conversion.
"""

import pandas as pd
import re


def parse_amount(amount_str):
    """Convert amount string like '$1,000.00' to float"""
    if pd.isna(amount_str) or amount_str == "":
        return 0.0
    # Remove dollar sign, commas, and convert to float
    cleaned = re.sub(r"[$,]", "", str(amount_str))
    return float(cleaned)


def read_donation_data():
    """Read and parse the CSV donation data"""
    # Read the CSV file starting from the actual data (no need to skip rows)
    df = pd.read_csv("../data.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert amount column to numeric
    df["Amount_Numeric"] = df["Amount"].apply(parse_amount)

    # Convert dates to datetime
    df["Submit Date"] = pd.to_datetime(df["Submit Date"])
    df["Year"] = df["Submit Date"].dt.year

    return df