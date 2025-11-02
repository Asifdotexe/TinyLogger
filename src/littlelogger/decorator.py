"""
The core decorator logic
"""

import functools
import inspect
import json
import time
import warnings
from typing import Any, Callable, Dict

from .constants import DEFAULT_LOG_FILE, RUNTIME_PRECISION, TIMESTAMP_FORMAT
from .exceptions import LoggerNonSerializableError, LoggerWriteError


def _get_func_args(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """
    Figures out the names and values of all arguments passed to a function.

    We need to capture the name of the arguments (e.g., max_depth) and not just their values (e.g., 5).
    This function handles the logic of binding *args and **kwargs to the function signature.

    :param func: The function called.
    :param args: The positional arguments passed to the function.
    :param kwargs: The keyword arguments passed to the function.
    :return: A dictionary of parameter names mapped to their values.
    """
    try:
        # Bind the positional and keyword arguments to the function signature
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        # Fill in any default values for arguments that weren't provided.
        bound_args.apply_defaults()
        # Arguments is an OrderedDict, we convert it into plain dict
        return dict(bound_args.arguments)
    except Exception:
        # This 'try...except' is a safety net. Some special functions (like ones built-in to C) can't be inspected.
        # If that happens, we don't want to crash. We just log the arguments in a "raw" format.
        warnings.warn(
            f"[LittleLogger Warning] Could not figure out argument names for "
            f"'{func.__name__}'. Logging them as raw '_args' and '_kwargs'.",
            stacklevel=3,
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
        # Convert the dictionary to a JSON string.
        json_string = json.dumps(entry)
        return json_string + "\n"
    except TypeError as e:
        # This 'except' catches the failure from `json.dumps`.
        # This happens if the user's function returned something
        #   that isn't JSON-friendly (like a model object or a DataFrame).
        # We re-raise this as our own custom error so the decorator can catch it and handle it gracefully.
        raise LoggerNonSerializableError(e) from e


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

            This function is what actually replaces the user's original function. It captures arguments,
            runs the function, captures the result, and writes to the log.

            :param args: Positional arguments passed to the wrapped function.
            :param kwargs: Keyword arguments passed to the wrapped function.
            :return: The original return value of the wrapped function.
            """
            start_time = time.perf_counter()

            # We do this before running the function, just in case the function itself fails.
            func_args = _get_func_args(func, *args, **kwargs)

            try:
                # Run the user's original function
                result = func(*args, **kwargs)
            finally:
                # A 'finally' block always runs, even if the function in the 'try' block crashed.
                # This guarantees we always log how long it took.
                end_time = time.perf_counter()
                runtime = end_time - start_time

            # Put all the log information into a dictionary
            log_entry = {
                "timestamp": time.strftime(TIMESTAMP_FORMAT, time.gmtime()),
                "function_name": func.__name__,
                "runtime_seconds": round(runtime, RUNTIME_PRECISION),
                "params": func_args,
                "metrics": result,
            }

            # try to write this log to the file. This whole section is wrapped in a 'try...except'
            # so that if logging fails, it won't crash the user's script.
            try:
                # Convert the dictionary to a JSON string
                json_string = _serialize_log_entry(log_entry)

                try:
                    with open(
                        # 'a' means "append" (add to the end of the file).
                        # 'utf-8' is a standard text format.
                        log_file,
                        "a",
                        encoding="utf-8",
                    ) as f:
                        f.write(json_string)
                except (IOError, OSError) as e:
                    # This catches file system errors, like if the disk is full or we don't have permission to write.
                    raise LoggerWriteError(f"Failed to write log to file: {e}") from e

            except (LoggerNonSerializableError, LoggerWriteError) as e:
                # NOTE: MOST IMPORTANT RULE: Never crash the user's script.
                # If logging failed (for any reason), we just
                # show a warning and let the user's script continue.

                # 'stacklevel=2' tells the warning to point to the
                # line in the user's code that called this function,
                # which is much more helpful for debugging.
                warnings.warn(f"[LittleLogger Warning] {e}", stacklevel=2)

            return result

        return wrapper

    return decorator
