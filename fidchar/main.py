#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.
Coordinates data processing, analysis, visualization, and reporting.
"""

import os
import shutil
import yaml
from fidchar.core import data_processing as dp
from fidchar.core import analysis as an
from fidchar.core import visualization as vis
from fidchar.reports import charity_evaluator as ev
from fidchar.reports import html_report_builder as hrb
from fidchar.reports import base_report_builder as brb


def load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: {config_path} not found, using defaults")
        return {
            "input_file": "../data.csv",
            "output_dir": "../output",
            "sections": [],
            "charapi_config_path": None
        }


def main():
    """Main entry point for donation analysis."""
    try:
        config = load_config()

        # Resolve paths relative to current working directory (not package directory)
        input_file = config["input_file"]
        output_dir = config["output_dir"]

        # If paths are relative, they're relative to cwd
        if not os.path.isabs(input_file):
            input_file = os.path.abspath(input_file)
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)

        # Clean output directory before generating new reports
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print("Cleaned output directory")

        # Read the donation data
        print(f"Processing input file: {input_file}")
        df = dp.read_donation_data(input_file)

        # Analyze by category
        category_totals = an.analyze_by_category(df)

        # Analyze by year
        yearly_amounts, yearly_counts = an.analyze_by_year(df)

        # Create histograms
        vis.create_yearly_histograms(yearly_amounts, yearly_counts, output_dir)

        # Analyze donation patterns
        one_time, stopped_recur = an.analyze_donation_patterns(df)

        # Get all charities for evaluation (we'll filter later)
        top_n = config.get("top_charities_count", 10)

        # Get ALL charities by donation amount (not limited yet)
        all_charities = df.groupby("Tax ID").agg({
            "Amount_Numeric": "sum",
            "Organization": "first"
        }).sort_values("Amount_Numeric", ascending=False)

        # Get charity evaluations for ALL charities (includes recurring determination)
        charapi_cfg_path = config.get("charapi_config_path")
        recurring_config = config.get("recurring_charity")
        char_evals, recurring_ein_set, pattern_based_ein_set = ev.get_charity_evaluations(
            all_charities, charapi_cfg_path, df, recurring_config, one_time, stopped_recur
        )

        # Filter by minimum grant amount
        min_grant = config.get("top_charities_min_grant", 1000)
        filtered_charities = all_charities[all_charities["Amount_Numeric"] >= min_grant]

        # Get top N from filtered list
        top_charities = filtered_charities.head(top_n)

        # Sort based on configuration
        sort_order = config.get("top_charities_sort", "alpha")
        if sort_order == "alpha":
            top_charities = top_charities.sort_values("Organization")
        elif sort_order == "total_grant":
            top_charities = top_charities.sort_values("Amount_Numeric", ascending=False)
        else:
            # Default to alphabetical if invalid sort order
            top_charities = top_charities.sort_values("Organization")

        # Get detailed info for the filtered charities
        char_details = an.get_charity_details(df, top_charities)
        graph_info = vis.create_charity_yearly_graphs(top_charities, char_details, output_dir)

        # Generate HTML report
        print("Generating HTML report...")

        html_bldr = hrb.HTMLReportBuilder(df, config, char_details, graph_info, char_evals, recurring_ein_set, pattern_based_ein_set)
        html_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                    stopped_recur, top_charities)

        print("Report generated: donation_analysis.html in the output directory")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error processing data: {e}")
        raise


def _get_section_options(config: dict, section_name: str) -> dict:
    """Helper to extract section options from config."""
    for section in config.get("sections", []):
        if isinstance(section, dict) and section.get("name") == section_name:
            return section.get("options", {})
    return {}


if __name__ == "__main__":
    main()
