"""
A simple benchmark for LittleLogger's performance overhead.
"""

import os
import tempfile
import time
from timeit import timeit

from littlelogger import log_run

temp_file_descriptor, LOG_FILE = tempfile.mkstemp(suffix=".jsonl")
os.close(temp_file_descriptor)


def fast_function():
    """
    A non-decorated function
    """
    pass


@log_run(log_file=LOG_FILE)
def decorated_fast_function():
    """
    A function decorated with @log_run
    """
    pass


def slow_function():
    """
    A function that simulates 10ms of work.
    """
    time.sleep(0.01)


@log_run(log_file=LOG_FILE)
def decorated_slow_function():
    """
    A function that simulates 10ms of work.
    """
    time.sleep(0.01)


NUM_OF_RUNS = 100

# testing the fast function
time_fast = timeit(fast_function, number=NUM_OF_RUNS)
time_fast_decorated = timeit(decorated_fast_function, number=NUM_OF_RUNS)

# testing the slow function
time_slow = timeit(slow_function, number=NUM_OF_RUNS)
time_slow_decorated = timeit(decorated_slow_function, number=NUM_OF_RUNS)


# Calculating run overhead
per_run_overhead_fast_ms = ((time_fast_decorated - time_fast) / NUM_OF_RUNS) * 1000
per_run_overhead_slow_ms = ((time_slow_decorated - time_slow) / NUM_OF_RUNS) * 1000

# Calculating percentage
percentage_slowdown_fast = (time_fast_decorated - time_fast) / (time_fast + 1e-9) * 100
percentage_slowdown_slow = (time_slow_decorated - time_slow) / time_slow * 100

print("\n High Frequency Function (e.g., a 'pass' statement)")
print(
    f"\n Baseline (no log): {time_fast / NUM_OF_RUNS * 1_000_000:,.2f} microseconds per run"
)
print(
    f"\n With @log_run: {time_fast_decorated / NUM_OF_RUNS * 1_000_000:,.2f} microseconds per run"
)
print(f"\n Overhead: +{per_run_overhead_fast_ms:.2f} milliseconds per run")
print(f"\n This is a {percentage_slowdown_fast:,.0f}% slowdown.")

print("\n Slow Function (e.g., 'time.sleep(10ms)'")
print(
    f"\n Baseline (no log): {time_slow / NUM_OF_RUNS * 1_000_000:,.2f} microseconds per run"
)
print(
    f"\n With @log_run: {time_slow_decorated / NUM_OF_RUNS * 1_000_000:,.2f} microseconds per run"
)
print(f"\n Overhead: +{per_run_overhead_slow_ms:.2f} milliseconds per run")
print(f"\n This is a {percentage_slowdown_slow:,.1f}% slowdown.")

# Clean up the log file
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
print(f"\nCleaned up {LOG_FILE}")
