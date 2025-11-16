"""
TinyLogger: A lightweight, zero-setup decorator for logging ML experiments.
"""
from .decorator import log_run
from .util import load_log

__version__ = "1.1.1"

__all__ = ["log_run", "load_log"]