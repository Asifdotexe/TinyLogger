"""
Tests for the tinylogger package.
"""

import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from tinylogger.decorator import log_run


@log_run(log_file="test_log.jsonl")
def simple_model(param_a, param_b=10):
    """A simple function to test argument logging."""
    metric = param_a * param_b
    return {"metric": metric}


@log_run(log_file="test_log.jsonl")
def non_serializable_model():
    """A function that returns non-serializable data."""
    # object() is not JSON-serializable
    return {"metric": object()}


@pytest.fixture(name="clean_log_file")
def fixture_clean_log_file(tmp_path):
    """
    A pytest fixture that provides a temporary, clean log file path.

    We use `tmp_path` so that pytest handles creating and
    deleting test files. We never write test files to the
    actual project directory.
    """
    # tmp_path is a Pathlib object.
    file_path = tmp_path / "test_log.jsonl"
    return str(file_path)


def test_log_file_created_and_written(clean_log_file):
    """
    Test that a log file is created and the content is correct.
    """

    # We need to create a new decorated function that uses the *clean* log file
    @log_run(log_file=clean_log_file)
    def model(x):
        return {"y": x * 2}

    model(x=10)

    # Now, read the file and check its contents
    with open(clean_log_file, "r", encoding="utf-8") as f:
        log_line = f.readline()

    assert log_line, "Log file is empty"

    data = json.loads(log_line)

    assert data["function_name"] == "model"
    assert data["params"] == {"x": 10}
    assert data["metrics"] == {"y": 20}
    assert "timestamp" in data
    assert "runtime_seconds" in data


def test_log_correct_arguments(clean_log_file):
    """
    Test that positional, keyword, and default args are all logged.
    """

    @log_run(log_file=clean_log_file)
    def model(a, b=10, _c="test"):
        return {"metric": a + b}

    # a=5, b=10 (default), _c="override"
    model(5, _c="override")

    # Read the log
    df = pd.read_json(clean_log_file, lines=True)
    assert len(df) == 1

    params = df.iloc[0]["params"]
    assert params == {"a": 5, "b": 10, "_c": "override"}


def test_multiple_runs_append_to_file(clean_log_file):
    """
    Test that multiple calls to the decorated function append
    new lines to the same file.
    """

    @log_run(log_file=clean_log_file)
    def model(val):
        return {"val": val}

    model(1)
    model(2)
    model(3)

    # Read the log
    df = pd.read_json(clean_log_file, lines=True)
    assert len(df) == 3
    assert df["metrics"].apply(lambda d: d["val"]).tolist() == [1, 2, 3]


def test_logging_failure_does_not_crash():
    """
    CRITICAL: Test that if logging fails, the user's function
    still returns its value and a warning is issued.
    """
    # We patch `open` to raise a PermissionError when called.
    # This simulates a file system error.
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = PermissionError("Permission denied")

        # We must use `pytest.warns` to check that our warning was issued.
        with pytest.warns(UserWarning, match="Failed to log run"):

            @log_run(log_file="any_file.jsonl")
            def model(x):
                return x * 2

            result = model(10)

    # The most important part: the original function's value
    # was still returned, even though logging failed.
    assert result == 20


def test_non_serializable_metrics_does_not_crash(clean_log_file):
    """
    Test that non-serializable return values are handled gracefully.
    """

    @log_run(log_file=clean_log_file)
    def model():
        return {"metric": object()}  # Not serializable

    # We check that a warning is issued and the script doesn't crash
    with pytest.warns(UserWarning, match="Failed to serialize"):
        result = model()

    # The original (non-serializable) result is still returned
    assert isinstance(result["metric"], object)

    # The log file should be empty, as the write failed
    with open(clean_log_file, "r", encoding="utf-8") as f:
        assert f.read() == ""
