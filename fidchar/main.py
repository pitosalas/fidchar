#!/usr/bin/env python3
"""Main orchestration module for charitable donation analysis.
Coordinates data processing, analysis, visualization, and reporting.

HYDRA VERSION - demonstrates Hydra configuration management
"""

import os
import shutil
import hydra
from omegaconf import DictConfig, OmegaConf
import core.data_processing as dp
import core.analysis as an
import core.visualization as vis
import reports.markdown_report_builder as mrb
import reports.text_report_builder as trb
import reports.charity_evaluator as ev
import reports.html_report_builder as hrb


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """Main entry point with Hydra configuration.

    Args:
        cfg: Hydra configuration object (auto-injected)

    Usage examples:
        # Run with default config
        python main.py

        # Override config values from CLI
        python main.py input_file=../data2.csv
        python main.py generate_html=false generate_markdown=true
        python main.py sections[2].options.min_years=15

        # Multi-run with different parameters
        python main.py -m sections[2].options.min_years=5,10,15
    """
    try:
        # Hydra changes working directory - get original paths
        input_file = cfg.input_file
        output_dir = cfg.output_dir

        # Convert to absolute paths if needed
        if not os.path.isabs(input_file):
            input_file = os.path.join(hydra.utils.get_original_cwd(), input_file)
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(hydra.utils.get_original_cwd(), output_dir)

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

        # Extract config for recurring donations
        recur_cfg = _get_section_options(cfg, "recurring")
        sort_by = recur_cfg.get("sort_by", "total")
        min_yrs_recur = recur_cfg.get("min_years", 4)
        recur_donations = an.analyze_recurring_donations(df, sort_by, min_yrs_recur, 4)

        # Analyze top charities using config
        top_char_cfg = _get_section_options(cfg, "top_charities")
        top_n = top_char_cfg.get("count", 10)
        app_id = cfg.charity_navigator.app_id
        app_key = cfg.charity_navigator.app_key or os.getenv("CHARITY_NAVIGATOR_APP_KEY")
        top_charities, char_details, char_descs, graph_info = dp.analyze_top_charities(
            df, top_n, app_id, app_key)

        # Get charity evaluations from charapi (includes focus determination)
        charapi_cfg_path = cfg.get("charapi_config_path")
        if charapi_cfg_path and not os.path.isabs(charapi_cfg_path):
            charapi_cfg_path = os.path.join(hydra.utils.get_original_cwd(), charapi_cfg_path)
        char_evals, focus_ein_set = ev.get_charity_evaluations(top_charities, charapi_cfg_path, df)

        # Create analysis visualizations
        print("Creating analysis visualizations...")
        vis.create_efficiency_frontier(df, char_evals)

        # Generate reports
        print("Generating reports...")

        # Convert OmegaConf to plain dict for compatibility with existing code
        config_dict = OmegaConf.to_container(cfg, resolve=True)

        if cfg.generate_html:
            html_bldr = hrb.HTMLReportBuilder(df, config_dict, char_details, char_descs, graph_info, char_evals, focus_ein_set)
            html_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                        stopped_recur, top_charities, recur_donations)

        if cfg.generate_markdown:
            md_bldr = mrb.MarkdownReportBuilder(df, config_dict, char_details, char_descs, graph_info, char_evals, focus_ein_set)
            md_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                            stopped_recur, top_charities, recur_donations)

        if cfg.generate_textfile:
            txt_bldr = trb.TextReportBuilder(df, config_dict, char_details, char_descs, graph_info, char_evals, focus_ein_set)
            txt_bldr.generate_report(category_totals, yearly_amounts, yearly_counts, one_time,
                                        stopped_recur, top_charities, recur_donations)

        files_generated = []
        if cfg.generate_html:
            files_generated.append("donation_analysis.html")
        if cfg.generate_markdown:
            files_generated.append("donation_analysis.md")
        if cfg.generate_textfile:
            files_generated.append("donation_analysis.txt")

        print(f"Reports generated: {', '.join(files_generated)} in the output directory")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error processing data: {e}")
        raise


def _get_section_options(cfg: DictConfig, section_name: str) -> dict:
    """Helper to extract section options from config.

    Cleaner than the old next() approach with list comprehension!
    """
    for section in cfg.sections:
        if isinstance(section, DictConfig) and section.get("name") == section_name:
            return section.get("options", {})
    return {}


if __name__ == "__main__":
    main()
