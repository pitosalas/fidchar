#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.

Coordinates data processing, analysis, visualization, and reporting.
"""

import os
import shutil
import yaml
from core.data_processing import read_donation_data
from core.analysis import (
    analyze_by_category, analyze_by_year, analyze_donation_patterns,
    get_top_charities_basic, get_charity_details, analyze_consistent_donors
)
from core.visualization import create_yearly_histograms, create_charity_yearly_graphs
from reports.reporting import generate_console_report, get_charity_descriptions
from reports.report_builder import generate_markdown_report
from reports.text_report_builder import generate_text_report
from reports.charity_evaluator import get_charity_evaluations


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


def load_config():
    """Load configuration from YAML file"""
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print("Warning: config.yaml not found, using defaults")
        return {
            "input_file": "../data.csv",
            "generate_html": False,
            "generate_markdown": False,
            "generate_textfile": True,
            "sections": [1, 2, 3, 4, 5, 6, 7],
            "output_dir": "../output",
            "charity_navigator": {"app_id": "3069", "app_key": None}
        }


def main():
    """Main program execution"""
    try:
        # Load configuration
        config = load_config()
        input_file = config["input_file"]
        generate_html = config.get("generate_html", config.get("generate_pdf", False))
        output_dir = config["output_dir"]

        # Clean output directory before generating new reports
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print("Cleaned output directory")

        # Read the donation data
        print(f"Processing input file: {input_file}")
        df = read_donation_data(input_file)

        # Analyze by category
        category_totals = analyze_by_category(df)

        # Analyze by year
        yearly_amounts, yearly_counts = analyze_by_year(df)

        # Create histograms
        create_yearly_histograms(yearly_amounts, yearly_counts)

        # Analyze donation patterns
        one_time, stopped_recurring = analyze_donation_patterns(df)

        # Analyze consistent donors over last 5 years
        consistent_donors = analyze_consistent_donors(df)

        # Analyze top charities using config
        app_id = config["charity_navigator"]["app_id"]
        app_key = config["charity_navigator"]["app_key"] or os.getenv("CHARITY_NAVIGATOR_APP_KEY")
        top_charities, charity_details, charity_descriptions, graph_info = analyze_top_charities(
            df, app_id=app_id, app_key=app_key
        )

        # Get charity evaluations from charapi
        charapi_config_path = config.get("charapi_config_path")
        charity_evaluations = get_charity_evaluations(top_charities, charapi_config_path)

        # Generate reports
        print("Generating reports...")
        if config.get("generate_markdown", False):
            generate_markdown_report(
                category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring,
                top_charities, charity_details, charity_descriptions, graph_info, consistent_donors,
                charity_evaluations, config
            )

        if config.get("generate_textfile", False):
            generate_text_report(
                category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring,
                top_charities, charity_details, charity_descriptions, graph_info, consistent_donors,
                charity_evaluations, config
            )

        print("Reports generated:")
        if generate_html:
            print("  - ../output/comprehensive_report.html")
        if config.get("generate_markdown", False):
            print("  - ../output/donation_analysis.md")
        if config.get("generate_textfile", False):
            print("  - ../output/donation_analysis.txt")
        print("  - Various PNG charts")

        # Generate PDF from HTML (if enabled in config)
        if generate_html:
            print("PDF generation available - use 'Print to PDF' from your browser")
            print(f"Open: {output_dir}/comprehensive_report.html in your browser")
        else:
            print("HTML generation disabled in config.yaml")

    except FileNotFoundError:
        print("Error: data.csv file not found")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()