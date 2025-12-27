#!/usr/bin/env python3
"""Quick performance analysis with timing of major sections.

Usage:
    uv run python analyze_performance.py
"""

import time
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fidchar'))

# Monkey-patch to track function calls
call_counts = defaultdict(int)
call_times = defaultdict(float)

def track_calls(func):
    """Decorator to track function calls and timing"""
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__qualname__}"
        call_counts[func_name] += 1

        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start

        call_times[func_name] += elapsed
        return result
    return wrapper

def patch_functions():
    """Patch key functions to track their performance"""
    from fidchar.reports import base_report_builder as brb
    from fidchar.reports import html_report_builder as hrb
    from fidchar.reports import charity_evaluator as ce

    # Patch BaseReportBuilder methods
    brb.BaseReportBuilder.format_charity_info = track_calls(brb.BaseReportBuilder.format_charity_info)
    brb.BaseReportBuilder.for_consideration = track_calls(brb.BaseReportBuilder.for_consideration)
    brb.BaseReportBuilder.is_recurring_charity = track_calls(brb.BaseReportBuilder.is_recurring_charity)
    brb.BaseReportBuilder.get_alignment_status = track_calls(brb.BaseReportBuilder.get_alignment_status)

    # Patch HTMLReportBuilder methods
    hrb.HTMLReportBuilder.generate_charity_card_bootstrap = track_calls(hrb.HTMLReportBuilder.generate_charity_card_bootstrap)
    hrb.HTMLReportBuilder.generate_top_charities_bootstrap = track_calls(hrb.HTMLReportBuilder.generate_top_charities_bootstrap)
    hrb.HTMLReportBuilder.generate_one_time_table_bootstrap = track_calls(hrb.HTMLReportBuilder.generate_one_time_table_bootstrap)
    hrb.HTMLReportBuilder.generate_stopped_table_bootstrap = track_calls(hrb.HTMLReportBuilder.generate_stopped_table_bootstrap)

    # Patch charity_evaluator
    ce.get_charity_evaluations = track_calls(ce.get_charity_evaluations)

def main():
    """Run with performance tracking"""
    patch_functions()

    from fidchar import main as fidchar_main

    print("="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    print("Running fidchar with performance tracking...\n")

    overall_start = time.time()

    try:
        fidchar_main.main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    overall_time = time.time() - overall_start

    print("\n" + "="*80)
    print("PERFORMANCE RESULTS")
    print("="*80)
    print(f"\nTotal execution time: {overall_time:.2f}s\n")

    # Sort by total time
    sorted_by_time = sorted(call_times.items(), key=lambda x: x[1], reverse=True)

    print("TOP FUNCTIONS BY TOTAL TIME:")
    print("-" * 80)
    print(f"{'Function':<60} {'Calls':>8} {'Total(s)':>10}")
    print("-" * 80)
    for func_name, total_time in sorted_by_time[:20]:
        count = call_counts[func_name]
        avg_time = total_time / count if count > 0 else 0
        short_name = func_name.split('.')[-1] if '.' in func_name else func_name
        module = func_name.rsplit('.', 1)[0] if '.' in func_name else ''
        display_name = f"{module[-40:]}.{short_name}" if len(module) > 40 else func_name
        print(f"{display_name:<60} {count:>8} {total_time:>10.3f}")

    print("\n" + "="*80)
    print("TOP FUNCTIONS BY CALL COUNT:")
    print("-" * 80)
    print(f"{'Function':<60} {'Calls':>8} {'Avg(ms)':>10}")
    print("-" * 80)
    sorted_by_calls = sorted(call_counts.items(), key=lambda x: x[1], reverse=True)
    for func_name, count in sorted_by_calls[:20]:
        total_time = call_times[func_name]
        avg_time = (total_time / count * 1000) if count > 0 else 0
        short_name = func_name.split('.')[-1] if '.' in func_name else func_name
        module = func_name.rsplit('.', 1)[0] if '.' in func_name else ''
        display_name = f"{module[-40:]}.{short_name}" if len(module) > 40 else func_name
        print(f"{display_name:<60} {count:>8} {avg_time:>10.3f}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("-" * 80)

    # Identify potential issues
    for func_name, count in call_counts.items():
        if count > 1000:
            total_time = call_times[func_name]
            print(f"⚠️  {func_name}: called {count:,} times (consider caching/optimization)")

        avg_time = (call_times[func_name] / count) if count > 0 else 0
        if avg_time > 0.1:  # Slower than 100ms per call
            print(f"🐌 {func_name}: avg {avg_time*1000:.1f}ms per call (consider optimization)")

    print("="*80)


if __name__ == '__main__':
    main()
