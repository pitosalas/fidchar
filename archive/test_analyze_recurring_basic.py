#!/usr/bin/env python3
"""Focused tests for analyze_recurring_donations (legacy scenarios).

These tests were originally written for a simplified implementation. The
current production implementation now:
    * Detects recurring donations via the 'Recurring' text column
    * Derives a Period (e.g. "2021-2024") and Last_Donation_Date
    * Filters out charities whose most recent donation is considered stale

We keep these lightweight structural tests by simply ensuring the fabricated
rows include a 'Recurring' value so they are considered by the newer logic.
Expectations that still hold:
    * At least `min_years` distinct years (default 4) required for inclusion
    * Average annual amount = total / years
    * Default sort is by total donated descending (unless sort_by="annual")
"""

import pandas as pd
from datetime import datetime
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fidchar'))
from core.analysis import analyze_recurring_donations


def build_df(rows):
    return pd.DataFrame(rows)


def test_returns_empty_when_no_charity_reaches_min_years():
    current_year = datetime.now().year
    df = build_df([
        {"Tax ID": "11", "Organization": "A", "Amount_Numeric": 100, "Year": current_year, "Submit Date": pd.Timestamp(f"{current_year}-01-10"), "Recurring": "Annually"},
        {"Tax ID": "22", "Organization": "B", "Amount_Numeric": 200, "Year": current_year-1, "Submit Date": pd.Timestamp(f"{current_year-1}-02-10"), "Recurring": "Annually"},
    ])
    result = analyze_recurring_donations(df, "total", 4, 4)
    assert result.empty


def test_includes_charity_with_four_years():
    current_year = datetime.now().year
    rows = []
    for offset, amount in enumerate([100, 150, 200, 250]):
        rows.append({
            "Tax ID": "11", "Organization": "A", "Amount_Numeric": amount,
            "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-03-15"),
            "Recurring": "Annually"
        })
    df = build_df(rows)
    result = analyze_recurring_donations(df, "total", 4, 4)
    assert len(result) == 1
    row = result.iloc[0]
    assert row['EIN'] == '11'
    assert row['Years_Supported'] == 4
    assert row['First_Year'] == current_year - 3
    assert pytest.approx(row['Amount'], 0.01) == sum([100,150,200,250]) / 4
    assert row['Total_Ever_Donated'] == 700


def test_sorts_by_total_descending_when_multiple():
    current_year = datetime.now().year
    rows = []
    # Charity 11: 4 years totaling 400
    for offset, amount in enumerate([100, 100, 100, 100]):
        rows.append({"Tax ID": "11", "Organization": "A", "Amount_Numeric": amount, "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-01-01"), "Recurring": "Annually"})
    # Charity 22: 4 years totaling 800
    for offset, amount in enumerate([200, 200, 200, 200]):
        rows.append({"Tax ID": "22", "Organization": "B", "Amount_Numeric": amount, "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-02-01"), "Recurring": "Annually"})

    df = build_df(rows)
    result = analyze_recurring_donations(df, "total", 4, 4)
    assert list(result['EIN']) == ['22', '11']


def test_respects_sort_by_annual():
    current_year = datetime.now().year
    rows = []
    # Charity 11: 4 years amounts increasing -> avg 162.5 total 650
    for offset, amount in enumerate([100, 150, 200, 200]):
        rows.append({"Tax ID": "11", "Organization": "A", "Amount_Numeric": amount, "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-01-05"), "Recurring": "Annually"})
    # Charity 22: 4 years flat 150 -> avg 150 total 600
    for offset in range(4):
        rows.append({"Tax ID": "22", "Organization": "B", "Amount_Numeric": 150, "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-02-05"), "Recurring": "Annually"})

    df = build_df(rows)
    result = analyze_recurring_donations(df, "annual", 4, 4)
    # 11 should come before 22 because 162.5 > 150
    assert list(result['EIN']) == ['11', '22']


def test_ignores_extra_columns_if_present():
    current_year = datetime.now().year
    rows = []
    for offset, amount in enumerate([50, 50, 50, 50]):
        rows.append({"Tax ID": "X", "Organization": "XOrg", "Amount_Numeric": amount, "Year": current_year - offset, "Submit Date": pd.Timestamp(f"{current_year - offset}-04-01"), "Unused": "ignore", "Recurring": "Annually"})
    df = build_df(rows)
    result = analyze_recurring_donations(df, "total", 4, 4)
    assert 'Unused' not in result.columns
    assert len(result) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
