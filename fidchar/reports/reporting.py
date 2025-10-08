#!/usr/bin/env python3
"""Reporting module for charitable donation analysis.

Handles API calls, report generation, and file output.
"""

import requests
import time

def get_charity_description(tax_id, app_id=None, app_key=None):
    """Fetch charity description from Charity Navigator API"""
    if not app_id or not app_key:
        return "API credentials not configured"

    try:
        # Format tax ID (remove dashes)
        clean_tax_id = tax_id.replace("-", "") if tax_id else ""

        # Charity Navigator API endpoint
        url = f"https://api.data.charitynavigator.org/v2/Organizations/{clean_tax_id}"
        params = {
            "app_id": app_id,
            "app_key": app_key
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return _extract_charity_mission(data)

        elif response.status_code == 404:
            return "Organization not found in Charity Navigator"
        else:
            return f"API error: {response.status_code}"

    except Exception as e:
        return f"Error fetching description: {str(e)}"


def _extract_charity_mission(data):
    """Extract mission or description from API response"""
    # Extract mission or description from the response
    mission = data.get("mission")
    if mission:
        return mission

    # Fallback to other description fields
    cause = data.get("cause", {})
    if isinstance(cause, dict):
        cause_name = cause.get("causeName", "")
        if cause_name:
            return f"Focuses on: {cause_name}"

    return "No description available"


def get_charity_descriptions(top_charities, app_id, app_key):
    """Fetch descriptions for all top charities"""
    charity_descriptions = {}

    for tax_id in top_charities.index:
        # Fetch charity description from API
        description = get_charity_description(tax_id, app_id, app_key)
        charity_descriptions[tax_id] = description

        # Add small delay to be respectful to API
        time.sleep(0.1)
    return charity_descriptions


def generate_console_report(category_totals):
    """Generate console report of category totals"""
    print("CHARITABLE DONATION ANALYSIS")
    print("=" * 40)
    print()
    print("Total Donations by Charitable Sector:")
    print("-" * 40)

    total_amount = 0
    for category, amount in category_totals.items():
        print(f"{category:<25} ${amount:>10,.2f}")
        total_amount += amount

    print("-" * 40)
    print(f"{'TOTAL':<25} ${total_amount:>10,.2f}")