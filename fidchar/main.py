#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.

Coordinates data processing, analysis, visualization, and reporting.
"""

import os
from data_processing import read_donation_data
from analysis import (
    analyze_by_category, analyze_by_year, analyze_donation_patterns,
    get_top_charities_basic, get_charity_details
)
from visualization import create_yearly_histograms, create_charity_yearly_graphs
from reporting import generate_console_report, get_charity_descriptions
from report_builder import generate_markdown_report


def analyze_top_charities(df, top_n=10, app_id=None, app_key=None):
    """Orchestrate top charities analysis with API integration"""
    # Get basic top charities data
    top_charities = get_top_charities_basic(df, top_n)

    # Get detailed donation history for each top charity
    charity_details = get_charity_details(df, top_charities)

    # Fetch charity descriptions from API
    charity_descriptions = get_charity_descriptions(top_charities, app_id, app_key)

    # Create yearly graphs for each charity (only if they have recent donations)
    graph_info = create_charity_yearly_graphs(top_charities, charity_details)

    return top_charities, charity_details, charity_descriptions, graph_info


def main():
    """Main program execution"""
    try:
        # Read the donation data
        df = read_donation_data()

        # Analyze by category
        category_totals = analyze_by_category(df)

        # Analyze by year
        yearly_amounts, yearly_counts = analyze_by_year(df)

        # Generate console report
        generate_console_report(category_totals)

        # Create histograms
        create_yearly_histograms(yearly_amounts, yearly_counts)

        # Analyze donation patterns
        one_time, stopped_recurring = analyze_donation_patterns(df)

        # Analyze top charities (add your Charity Navigator API credentials here)
        app_id = os.getenv("CHARITY_NAVIGATOR_APP_ID", "3069")  # Your app ID
        app_key = os.getenv("CHARITY_NAVIGATOR_APP_KEY")  # You need to provide the app_key
        top_charities, charity_details, charity_descriptions, graph_info = analyze_top_charities(
            df, app_id=app_id, app_key=app_key
        )

        # Generate markdown report
        generate_markdown_report(
            category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring,
            top_charities, charity_details, charity_descriptions, graph_info
        )

        print("\nReports generated in ../output/ directory")

    except FileNotFoundError:
        print("Error: data.csv file not found")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()