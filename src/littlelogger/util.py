"""
This module will house all the utility functions that would be used along with littlelogger
"""

from pathlib import Path
from typing import Union

import pandas as pd


def load_log(log_file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load and normalize the provided LittleLogger JSONL log file.

    :param log_file_path: Path to the log file
    :return: Pandas dataframe containing the log file in a normalized format
    """
    df = pd.read_json(log_file_path, lines=True)

    # Use json_normalize and then add_prefix
    df_params = pd.json_normalize(df["params"]).add_prefix("param_")
    df_metrics = pd.json_normalize(df["metrics"]).add_prefix("metric_")

    # Get the other columns we want
    df_main = df[["timestamp", "function_name", "runtime_seconds"]]

    # Join them all together into one clean DataFrame
    df = pd.concat([df_main, df_params, df_metrics], axis=1)

    # Re-order columns to group params and metrics for clarity
    all_cols = (
        list(df_main.columns)
        + sorted([c for c in df.columns if c.startswith("param_")])
        + sorted([c for c in df.columns if c.startswith("metric_")])
    )

    return df[all_cols]
