#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.
Coordinates data processing, analysis, visualization, and reporting.
"""

import os
import shutil
import yaml
import core.data_processing as dp
import core.analysis as an
import core.visualization as vis
import reports.charity_evaluator as ev
import reports.html_report_builder as hrb


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
        input_file = config["input_file"]
        output_dir = config["output_dir"]

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
        vis.create_yearly_histograms(yearly_amounts, yearly_counts)

        # Analyze donation patterns
        one_time, stopped_recur = an.analyze_donation_patterns(df)

        # Analyze top charities using config
        top_char_cfg = _get_section_options(config, "top_charities")
        top_n = top_char_cfg.get("count", 10)
        top_charities, char_details, graph_info = dp.analyze_top_charities(df, top_n)

        # Get charity evaluations from charapi (includes focus determination)
        charapi_cfg_path = config.get("charapi_config_path")
        char_evals, focus_ein_set = ev.get_charity_evaluations(top_charities, charapi_cfg_path, df)

        # Generate HTML report
        print("Generating HTML report...")

        html_bldr = hrb.HTMLReportBuilder(df, config, char_details, graph_info, char_evals, focus_ein_set)
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
