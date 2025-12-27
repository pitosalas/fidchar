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
import reports.markdown_report_builder as mrb
import reports.text_report_builder as trb
import reports.charity_evaluator as ev
import reports.html_report_builder as hrb


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
    try:
        # Load configuration
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

        # Analyze consistent donors with configured parameters
        consist_cfg = next((s.get("options", {}) for s in config.get("sections", [])
                                 if isinstance(s, dict) and s.get("name") == "consistent"), {})
        min_years = consist_cfg.get("min_years", 5)
        min_amount = consist_cfg.get("min_amount", 500)
        consist_donors = an.analyze_consistent_donors(df, min_years, min_amount)

        # Analyze recurring donations with configured parameters
        recur_cfg = next((s.get("options", {}) for s in config.get("sections", [])
                                if isinstance(s, dict) and s.get("name") == "recurring"), {})
        sort_by = recur_cfg.get("sort_by", "total")
        min_yrs_recur = recur_cfg.get("min_years", 4)
        recur_donations = an.analyze_recurring_donations(df, sort_by, min_yrs_recur, 4)

        # Analyze top charities using config
        app_id = config["charity_navigator"]["app_id"]
        app_key = config["charity_navigator"]["app_key"] or os.getenv("CHARITY_NAVIGATOR_APP_KEY")
        top_charities, char_details, char_descs, graph_info = dp.analyze_top_charities(
            df, 10, app_id, app_key)

        # Get charity evaluations from charapi
        charapi_cfg_path = config.get("charapi_config_path")
        char_evals = ev.get_charity_evaluations(top_charities, charapi_cfg_path)

        # Create analysis visualizations
        print("Creating analysis visualizations...")
        vis.create_efficiency_frontier(df, char_evals)

        # Generate reports
        print("Generating reports...")

        if config.get("generate_html", False):
            html_bldr = hrb.HTMLReportBuilder(df, config, char_details, char_descs, graph_info, char_evals)
            html_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                        stopped_recur, top_charities, consist_donors, recur_donations)

        if config.get("generate_markdown", False):
            md_bldr = mrb.MarkdownReportBuilder(df, config, char_details, char_descs, graph_info, char_evals)
            md_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                            stopped_recur, top_charities, consist_donors, recur_donations)

        if config.get("generate_textfile", False):
            txt_bldr = trb.TextReportBuilder(df, config, char_details, char_descs, graph_info, char_evals)
            txt_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                        stopped_recur, top_charities, consist_donors, recur_donations)

        files_generated = []
        if config.get("generate_html", False):
            files_generated.append("donation_analysis.html")
        if config.get("generate_markdown", False):
            files_generated.append("donation_analysis.md")
        if config.get("generate_textfile", False):
            files_generated.append("donation_analysis.txt")

        print(f"Reports generated: {', '.join(files_generated)} in the output directory")

    except FileNotFoundError:
        print("Error: data.csv file not found")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()