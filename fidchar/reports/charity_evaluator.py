#!/usr/bin/env python3
"""Charity evaluation integration using charapi.

Handles all charapi dependencies and evaluation calls.
"""

import yaml
import traceback
from charapi.api.charity_evaluator import batch_evaluate
import core.analysis as an

def get_charity_evaluations(top_charities, charapi_config_path, donation_df, recurring_config=None,
                           one_time=None, stopped_recurring=None):
    """Fetch charity evaluations from charapi for top charities

    Args:
        top_charities: DataFrame index of Tax IDs
        charapi_config_path: Path to charapi config file
        donation_df: DataFrame with YOUR donation data (for recurring determination)
        recurring_config: Dict with recurring_charity settings (count, min_years, min_amount)
                         If None, uses defaults: count=15, min_years=5, min_amount=1000
        one_time: DataFrame of one-time donations (indexed by Tax ID)
        stopped_recurring: DataFrame of stopped recurring donations (indexed by Tax ID)
    """
    if not charapi_config_path:
        return {}, set()

    if recurring_config.get("enabled", True):
        recurring_charities = an.determine_recurring_charities(
            donation_df,
            recurring_config.get("count", 15),
            recurring_config.get("min_years", 5),
            recurring_config.get("min_amount", 1000)
        )
        print(f"Identified {len(recurring_charities)} recurring charities")
    else:
        recurring_charities = set()

    evaluations = {}

    # Combine all charity lists to ensure all displayed charities are evaluated
    charities_to_evaluate = set(top_charities.index) | recurring_charities

    if one_time is not None:
        charities_to_evaluate |= set(one_time.index)

    if stopped_recurring is not None:
        charities_to_evaluate |= set(stopped_recurring.index)

    print(f"Evaluating {len(charities_to_evaluate)} charities (top + recurring + one-time + stopped)")

    # Convert set to list for batch processing
    charity_list = list(charities_to_evaluate)

    try:
        # Evaluate all charities at once with shared config/clients
        results = batch_evaluate(charity_list, charapi_config_path)

        # Convert list results to dict
        evaluations = {ein: result for ein, result in zip(charity_list, results)}

    except Exception as e:
        print(f"Warning: Batch evaluation failed: {e}")
        # Get the last frame from traceback (where the error actually occurred)
        tb_lines = traceback.format_exc().splitlines()
        # Find the actual source line (skip the error message at the end)
        for line in reversed(tb_lines[:-1]):
            if 'File "' in line or '.py", line' in line:
                print(f"  {line.strip()}")
                break

    return evaluations, recurring_charities
