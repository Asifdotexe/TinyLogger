"""
The core decorator logic
"""

import datetime
import functools
import inspect
import json
import warnings
from typing import Any, Callable, Dict

from .constants import DEFAULT_LOG_FILE
from .exceptions import LoggerNonSerializableError, LoggerWriteError


def _get_func_args(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """
    Maps all positonal and keyword arguments to their parameter names.

    We need to capture the name of the arguements (e.g., max_depth) and not just their values (e.g., 5).
    This function handles the logic of binding *args and **kwargs to the function signature.

    :param func: The function called.
    :param args: The positional arguments passed to the function.
    :param kwargs: The keyword arguements passed to the function.
    :return: A dictionary of parameter names mapped to their values.
    """
    try:
        # Bind the positional and keyword arguments to the function signature
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        # Apply the default for any missing arguements
        bound_args.apply_defaults()
        # Arguments is an OrderedDict, we convert it into plain dict
        return dict(bound_args.arguments)
    except Exception:
        # Fallback for complex callables where binding might fail.
        # this is less informative but safer than crashing.
        warnings.warn(
            f"[TinyLogger Warning] Could not inspect function "
            f"signature for '{func.__name__}'. "
            f"Logging raw positional and keyword args.",
            stacklevel=3
        )
        return {"_args": args, "_kwargs": kwargs}


def _serialize_log_entry(entry: Dict[str, Any]) -> str:
    """
    Converts a log entry dictionary into a JSONL-formatted string

    JSON-Lines (.jsonl) format requires each log entry to be a single, valid JSON object, followed by a newline.
    This function enforces that.

    :param entry: The dictionary containing log data.
    :return: A JSON string ending with a newline.
    """
    try:
        # NOTE: default=str is a safe fallback for common non-serializable types like datetime objects,
        # converting them to their string form.
        json_string = json.dumps(entry, default=str)
        return json_string + "\n"
    except TypeError as e:
        # We catch the specific `TypeError` from json.dumps and re-raise it as our custom, more informative exception.
        raise LoggerNonSerializableError(
            f"Failed to serialize log entry. "
            f"Your function's arguments or return value (metrics) "
            f"may contain objects that are not JSON-serializable. "
            f"Original error: {e}"
        ) from e

def log_run(log_file: str = DEFAULT_LOG_FILE) -> Callable[..., Any]:
    """
    A decorator factory that logs function calls to the JSONL file.

    :param log_file: The path to the .jsonl file for logging., defaults to DEFAULT_LOG_FILE
    :return: The decorator.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        The decorator that wraps the user's function.

        :param func: The function to be decorated.
        :return: The wrapped function.
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            The wrapper function that executes the logging logic.

            :return: The original return value of the decorated function.
            """
            start_time = datetime.datetime.now(datetime.timezone.utc)

            # We run the user's function first. If it fails, we don't want to log a "run" that never completed.
            try:
                metrics = func(*args, **kwargs)
            except Exception:
                # If the user's function fails, we re-raise the error immediately. No logging should happen.
                raise

            end_time = datetime.datetime.now(datetime.timezone.utc)
            runtime_seconds = (end_time - start_time).total_seconds()

            # The logging is a side-effect and must never crash the user's main script/
            try:
                # Capture parameters
                params = _get_func_args(func, *args, **kwargs)
                # Build the log entry
                log_entry: Dict[str, Any] = {
                    "timestamp": start_time.isoformat(),
                    "runtime_seconds": round(runtime_seconds, 4),
                    "params": params,
                    "metrics": metrics,
                    "function_name": func.__name__,
                }
                # Serialize to JSONL string
                log_line = _serialize_log_entry(log_entry)

                # Write to file
                # 'a' mode: Append to the file. Creates it if it doesn't exist.
                # 'encoding="utf-8"': The only sane choice for text files.
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_line)

            except (
                LoggerNonSerializableError,
                LoggerWriteError,
                IOError,
                PermissionError,
            ) as e:
                # We catch our custom errors and common file errors.
                # We use `warnings.warn` instead of `print` because
                # it's the standard way for libraries to signal non-fatal issues to a user.
                warnings.warn(
                    f"[TinyLogger Warning] Failed to log run. "
                    f"Your function's result was returned, but the log "
                    f"was NOT written. \nError: {e}",
                    stacklevel=2,
                )

            except Exception as e:
                # A "catch-all" for any other unexpected logging error.
                # This ensures nothing in the logging block can crash.
                warnings.warn(
                    f"[TinyLogger Warning] An unexpected error occurred "
                    f"during logging: {e}",
                    stacklevel=2,
                )

            return metrics

        return wrapper

    return decorator
