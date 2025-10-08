#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.
Coordinates data processing, analysis, visualization, and reporting.
"""

import os
import shutil
import yaml
import core.data_processing as cdp
import core.analysis as ca
import core.visualization as viz
import reports.markdown_report_builder as mark 
import reports.text_report_builder as txt
import reports.charity_evaluator as char
import reports.comprehensive_report as html
import tables.great_tables_builder as tab


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
        df = cdp.read_donation_data(input_file)

        # Analyze by category
        category_totals = ca.analyze_by_category(df)

        # Analyze by year
        yearly_amounts, yearly_counts = ca.analyze_by_year(df)

        # Create histograms
        viz.create_yearly_histograms(yearly_amounts, yearly_counts)

        # Analyze donation patterns
        one_time, stopped_recurring = ca.analyze_donation_patterns(df)

        # Analyze consistent donors with configured parameters
        consistent_config = next((s.get("options", {}) for s in config.get("sections", [])
                                 if isinstance(s, dict) and s.get("name") == "consistent"), {})
        min_years = consistent_config.get("min_years", 5)
        min_amount = consistent_config.get("min_amount", 500)
        consistent_donors = ca.analyze_consistent_donors(df, min_years, min_amount)

        # Analyze recurring donations with configured parameters
        recurring_config = next((s.get("options", {}) for s in config.get("sections", [])
                                if isinstance(s, dict) and s.get("name") == "recurring"), {})
        sort_by = recurring_config.get("sort_by", "total")
        min_years_recurring = recurring_config.get("min_years", 4)
        recurring_donations = ca.analyze_recurring_donations(df, sort_by, min_years_recurring, 4)

        # Analyze top charities using config
        app_id = config["charity_navigator"]["app_id"]
        app_key = config["charity_navigator"]["app_key"] or os.getenv("CHARITY_NAVIGATOR_APP_KEY")
        top_charities, charity_details, charity_descriptions, graph_info = cdp.analyze_top_charities(
            df, 10, app_id, app_key)

        # Get charity evaluations from charapi
        charapi_config_path = config.get("charapi_config_path")
        charity_evaluations = char.get_charity_evaluations(top_charities, charapi_config_path)

        # Create analysis visualizations
        print("Creating analysis visualizations...")
        viz.create_efficiency_frontier(df, charity_evaluations)

        # Generate reports
        print("Generating reports...")

        if config.get("generate_html", False):
            total_amount = category_totals.sum()
            html_report = html.create_comprehensive_html_report(
                category_totals, yearly_amounts, yearly_counts, consistent_donors,
                top_charities, total_amount, df, one_time, stopped_recurring,
                charity_details, charity_descriptions, graph_info
            )

            gt_categories = tab.create_gt_category_table(category_totals, total_amount)
            gt_yearly = tab.create_gt_yearly_table(yearly_amounts, yearly_counts)
            gt_consistent = tab.create_gt_consistent_donors_table(consistent_donors)
            gt_top_charities = tab.create_gt_top_charities_table(top_charities)

            consistent_total = sum(donor['total_5_year'] for donor in consistent_donors.values())
            html_report = html.add_table_sections_to_report(
                html_report, gt_consistent, gt_categories,
                gt_yearly, gt_top_charities, consistent_total, recurring_donations, config
            )

            html_report = html.add_detailed_charity_analysis(
                html_report, top_charities, charity_details, charity_descriptions,
                graph_info, charity_evaluations
            )
            with open(f"{output_dir}/comprehensive_report.html", "w") as f:
                f.write(html_report)

        if config.get("generate_markdown", False):
            markdown_builder = mark.MarkdownReportBuilder(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations)
            markdown_builder.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                            stopped_recurring, top_charities, consistent_donors, recurring_donations)

        if config.get("generate_textfile", False):
            text_builder = txt.TextReportBuilder(df, config, charity_details, charity_descriptions, graph_info, charity_evaluations)
            text_builder.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                        stopped_recurring, top_charities, consistent_donors, recurring_donations)

        files_generated = []
        if config.get("generate_html", False):
            files_generated.append("comprehensive_report.html")
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