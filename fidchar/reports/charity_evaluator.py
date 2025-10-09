#!/usr/bin/env python3
"""Charity evaluation integration using charapi.

Handles all charapi dependencies and evaluation calls.
"""

import time
import yaml
from charapi import evaluate_charity
import core.analysis as an

def get_charity_evaluations(top_charities, charapi_config_path, donation_df):
    """Fetch charity evaluations from charapi for top charities

    Args:
        top_charities: DataFrame index of Tax IDs
        charapi_config_path: Path to charapi config file
        donation_df: DataFrame with YOUR donation data (for focus determination)
    """
    if not charapi_config_path:
        return {}

    # Load charapi config to get focus_charity settings
    with open(charapi_config_path, "r") as f:
        charapi_config = yaml.safe_load(f)

    # Determine focus charities based on YOUR donation patterns using charapi config
    focus_cfg = charapi_config.get("focus_charity", {})
    if focus_cfg.get("enabled", False):
        focus_charities = an.determine_focus_charities(
            donation_df,
            focus_cfg.get("count", 15),
            focus_cfg.get("min_years", 5),
            focus_cfg.get("min_amount", 1000)
        )
        print(f"Identified {len(focus_charities)} focus charities")
    else:
        focus_charities = set()

    evaluations = {}

    for i, tax_id in enumerate(top_charities.index, 1):
        try:
            result = evaluate_charity(tax_id, charapi_config_path)

            # Override focus_charity flag with OUR determination based on YOUR donations
            result.focus_charity = tax_id in focus_charities

            evaluations[tax_id] = result
            time.sleep(0.1)
        except Exception as e:
            print(f"Warning: Could not evaluate charity {tax_id}: {e}")

    return evaluations, focus_charities
