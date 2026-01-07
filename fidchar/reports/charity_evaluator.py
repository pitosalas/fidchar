#!/usr/bin/env python3
"""Charity evaluation integration using charapi.

Handles all charapi dependencies and evaluation calls.
"""

import yaml
import traceback
from charapi.api.charity_evaluator import batch_evaluate
from fidchar.core import analysis as an


class CharityEvaluator:
    """Evaluates charities using charapi and determines recurring status."""

    def __init__(self, donation_df, config):
        """Initialize the charity evaluator.

        Args:
            donation_df: DataFrame with donation data for recurring determination
            config: Configuration dict containing charapi_config_path and recurring_charity settings
        """
        self.donation_df = donation_df
        self.charapi_config_path = config.get("charapi_config_path")
        self.recurring_config = config.get("recurring_charity", {})

    def get_evaluations(self, charities, one_time=None, stopped_recurring=None):
        """Fetch charity evaluations from charapi.

        Args:
            charities: DataFrame with charity data (indexed by Tax ID)
            one_time: DataFrame of one-time donations (indexed by Tax ID)
            stopped_recurring: DataFrame of stopped recurring donations (indexed by Tax ID)

        Returns:
            tuple: (evaluations_dict, recurring_ein_set, pattern_based_ein_set)
        """
        if not self.charapi_config_path:
            return {}, set(), set()

        recurring_charities = set()
        pattern_recurring = set()

        # Determine pattern-based recurring charities
        pattern_config = self.recurring_config.get("pattern_based", {})
        if pattern_config.get("enabled", False):
            pattern_recurring = an.get_recurring_by_pattern(
                self.donation_df,
                pattern_config.get("count", 15),
                pattern_config.get("min_years", 5),
                pattern_config.get("min_amount", 1000)
            )
            print(f"Identified {len(pattern_recurring)} pattern-based recurring charities")
            recurring_charities |= pattern_recurring

        # Determine CSV field-based recurring charities
        csv_config = self.recurring_config.get("csv_field_based", {})
        if csv_config.get("enabled", True):
            csv_recurring = an.get_recurring_by_csv_field(self.donation_df)
            print(f"Identified {len(csv_recurring)} CSV field-based recurring charities")
            recurring_charities |= csv_recurring

        print(f"Total recurring charities (combined): {len(recurring_charities)}")

        evaluations = {}

        # Combine all charity lists to ensure all displayed charities are evaluated
        charities_to_evaluate = set(charities.index) | recurring_charities

        if one_time is not None:
            charities_to_evaluate |= set(one_time.index)

        if stopped_recurring is not None:
            charities_to_evaluate |= set(stopped_recurring.index)

        print(f"Evaluating {len(charities_to_evaluate)} charities (all + recurring + one-time + stopped)")

        # Convert set to list for batch processing
        charity_list = list(charities_to_evaluate)

        try:
            # Evaluate all charities at once with shared config/clients
            results = batch_evaluate(charity_list, self.charapi_config_path)

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

        return evaluations, recurring_charities, pattern_recurring
