#!/usr/bin/env python3
"""Direct demo for progress bar functionality without test framework."""

import time
import sys
import os
import inspect

# Add the src directory to the path so we can import the progress module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from just.utils.progress import progress_bar, SimpleProgressBar


def iterable_usage_demo():
    """Demonstrate using progress bar as an iterator."""
    print("Processing items with progress bar as iterator...")

    # Using progress bar as an iterator (the original way)
    data = range(30)
    result = []
    for i in progress_bar(data, desc="Processing", unit="items"):
        # Simulate some work (0.05 seconds per item = 3 seconds total)
        time.sleep(0.05)
        result.append(i * 2)

    print(f"Processed {len(result)} items\n")


def context_manager_usage_demo():
    """Demonstrate using progress bar as a context manager."""
    print("Manual progress control with context manager...")

    # Using progress bar as a context manager
    with progress_bar(total=60, desc="Manual Progress", unit="tasks") as pbar:
        for i in range(60):
            # Simulate some work (0.05 seconds per item = 3 seconds total)
            time.sleep(0.05)
            # Manually update progress
            pbar.update(1)

    print("Manual progress completed\n")


def simple_mode_demo():
    """Demonstrate forcing simple mode."""
    print("Forcing simple text mode...")

    # Force simple mode
    data = range(60)
    for _ in progress_bar(data, desc="Simple Mode", mode="simple"):
        time.sleep(0.05)

    print("Simple mode completed\n")


def zero_total_demo():
    """Demonstrate progress bar with unknown total."""
    print("Progress bar with unknown total...")

    # Progress bar with unknown total, this should raise ValueError
    try:
        with progress_bar(total=0, desc="Processing", unit="items") as pbar:
            for i in range(60):
                time.sleep(0.05)
                pbar.update(1)
    except ValueError as e:
        print("ValueError:", e)

    print("Unknown total progress completed\n")


def direct_simple_progress_bar_demo():
    """Demonstrate direct usage of SimpleProgressBar."""
    print("Direct usage of SimpleProgressBar...")

    # Direct usage of SimpleProgressBar
    pb = SimpleProgressBar(total=60, desc="Direct Usage")
    pb.start()

    for i in range(60):
        time.sleep(0.05)
        pb.update(1)

    pb.close()
    print("Direct SimpleProgressBar completed\n")


def inspect_and_run_function(func):
    """Inspect and run a function to demonstrate its code."""
    print(f"{'='*60}")
    print(f"DEMO: {func.__name__}")
    print(f"{'='*60}")

    # Get the source code
    source = inspect.getsource(func)
    print("Source code:")
    print(source)
    print("\nExecution:")

    # Run the function
    start_time = time.time()
    func()
    end_time = time.time()

    print(f"Execution time: {end_time - start_time:.2f} seconds\n")


def main():
    """Main demonstration function."""
    print("Progress Bar Utilities Direct Demo")
    print("=" * 50)
    print("Each demo will take approximately 3 seconds to complete\n")

    # List of all demo functions
    demo_functions = [
        iterable_usage_demo,
        context_manager_usage_demo,
        simple_mode_demo,
        zero_total_demo,
        direct_simple_progress_bar_demo
    ]

    # Run all demos
    for func in demo_functions:
        inspect_and_run_function(func)

    print("=" * 60)
    print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()