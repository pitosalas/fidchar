"""
Charity Evaluation API

A comprehensive charity evaluation system that analyzes nonprofit organizations
using multiple data sources and provides scoring with letter grades.

Main entry points:
- evaluate_charity(ein, config_path): Evaluate a single charity by EIN
- batch_evaluate(eins, config_path): Evaluate multiple charities
"""

from .api.charity_evaluator import evaluate_charity, batch_evaluate
from .data.charity_evaluation_result import CharityEvaluationResult

__version__ = "1.0.0"
__all__ = ["evaluate_charity", "batch_evaluate", "CharityEvaluationResult"]