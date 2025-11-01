"""
Custom Exception for TinyLogger package
"""


class LoggerError(Exception):
    """
    Base exception for all the TinyLogger errors
    """

    pass


class LoggerNonSerializableError(TypeError, LoggerError):
    """
    Raised when the data passed to logger can't be serialized to JSON

    This helps distinguish between a user's `TypeError` and one that
    occurs specifically during the logging process.
    """
    
    DEFAULT_MESSAGE = (
        "Failed to serialize log entry. "
        "Ensure all arguments and return values are JSON-serializable."
    )


class LoggerWriteError(IOError, LoggerError):
    """
    Raised when logger fails to write the log file

    This could be due to several conditions:
        Permission
        Full disk
        Other file system issues
    """

    pass
