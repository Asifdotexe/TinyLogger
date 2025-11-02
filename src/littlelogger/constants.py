"""
Central place to hold all the constants
"""

# Default name for logfile when user provides none.
DEFAULT_LOG_FILE: str = "experiment_log.jsonl"

# The string format for timestamps in the log.
# This is the standard ISO 8601 format in UTC (Zulu time).
# Example: "2025-10-31T14:30:05Z"
TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

# The number of decimal places to round the runtime to.
RUNTIME_PRECISION: int = 6
