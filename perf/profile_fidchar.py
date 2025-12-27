#!/usr/bin/env python3
"""Profile fidchar to identify performance bottlenecks.

Usage:
    uv run python profile_fidchar.py
"""

import cProfile
import pstats
import io
import sys
import os

# Add fidchar to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fidchar'))

def profile_main():
    """Profile the main fidchar execution"""
    # Import here so it's included in profiling
    from fidchar import main

    # Run with profiling
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        main.main()
    except Exception as e:
        print(f"Error during profiling: {e}")
    finally:
        profiler.disable()

    # Print statistics
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)

    print("\n" + "="*80)
    print("TOP 50 FUNCTIONS BY CUMULATIVE TIME")
    print("="*80)
    ps.print_stats(50)
    print(s.getvalue())

    # Print by total time
    s = io.StringIO()
    sortby = pstats.SortKey.TIME
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)

    print("\n" + "="*80)
    print("TOP 50 FUNCTIONS BY TOTAL TIME")
    print("="*80)
    ps.print_stats(50)
    print(s.getvalue())

    # Print by number of calls
    s = io.StringIO()
    sortby = pstats.SortKey.CALLS
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)

    print("\n" + "="*80)
    print("TOP 30 MOST CALLED FUNCTIONS")
    print("="*80)
    ps.print_stats(30)
    print(s.getvalue())

    # Save detailed stats to file
    profiler.dump_stats('profile_results.prof')
    print("\n" + "="*80)
    print("Detailed profiling data saved to: profile_results.prof")
    print("View with: python -m pstats profile_results.prof")
    print("="*80)


if __name__ == '__main__':
    profile_main()
