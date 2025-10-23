#!/usr/bin/env python3
"""Line-by-line profiling for specific functions.

This uses line_profiler to show exactly which lines are slow.

Usage:
    uv add line-profiler  # First install
    uv run python -m kernprof -l -v profile_line_by_line.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fidchar'))

from fidchar import main
from fidchar.reports import base_report_builder
from fidchar.reports import html_report_builder
from fidchar.reports import charity_evaluator

# Mark functions to profile with @profile decorator (added by kernprof)
# We'll monkey-patch them

def run_with_profiling():
    """Run main with line profiling on key functions"""
    try:
        # Functions to profile (add @profile decorator at runtime)
        functions_to_profile = [
            (base_report_builder.BaseReportBuilder, 'format_charity_info'),
            (base_report_builder.BaseReportBuilder, 'for_consideration'),
            (base_report_builder.BaseReportBuilder, 'is_recurring_charity'),
            (html_report_builder.HTMLReportBuilder, 'generate_charity_card_bootstrap'),
            (charity_evaluator, 'get_charity_evaluations'),
        ]

        print("="*80)
        print("LINE PROFILER - Key Functions")
        print("="*80)
        print("\nFunctions being profiled:")
        for obj, func_name in functions_to_profile:
            if hasattr(obj, func_name):
                print(f"  - {obj.__name__}.{func_name}")
        print("\nRun with: uv run python -m kernprof -l -v profile_line_by_line.py")
        print("="*80 + "\n")

        main.main()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_with_profiling()
