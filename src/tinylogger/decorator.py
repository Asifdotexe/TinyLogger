"""
The core decorator logic
"""

import inspect
import json
from typing import Any, Callable, Dict

from .exceptions import LoggerNonSerializableError


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
        return {"args": args, "kwargs": kwargs}


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
            f"Ensure all arguments and return values are JSON-serializable. "
            f"Original error: {e}"
        ) from e
