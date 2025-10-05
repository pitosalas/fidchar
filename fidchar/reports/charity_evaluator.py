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

    for i, tax_id in enumerate(top_charities.index, 1):
        try:
            result = evaluate_charity(tax_id, charapi_config_path)
            evaluations[tax_id] = result
            time.sleep(0.1)
        except Exception as e:
            evaluations[tax_id] = None

    return evaluations
