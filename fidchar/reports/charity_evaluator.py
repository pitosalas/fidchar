#!/usr/bin/env python3
"""Charity evaluation integration using charapi.

Handles all charapi dependencies and evaluation calls.
"""

import time
from charapi import evaluate_charity


def get_charity_evaluations(top_charities, charapi_config_path):
    """Fetch charity evaluations from charapi for top charities"""
    if not charapi_config_path:
        return {}

    evaluations = {}
    print("Evaluating charities with charapi...")

    for i, tax_id in enumerate(top_charities.index, 1):
        print(f"  Evaluating {i}/{len(top_charities)}: {tax_id}", flush=True)
        try:
            result = evaluate_charity(tax_id, charapi_config_path)
            evaluations[tax_id] = result
            time.sleep(0.1)
        except Exception as e:
            print(f"    Warning: Could not evaluate {tax_id}: {str(e)}")
            evaluations[tax_id] = None

    return evaluations
