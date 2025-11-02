"""
Custom Exception for LittleLogger package
"""


class LoggerError(Exception):
    """
    Base exception for all the LittleLogger errors
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


    def __init__(self, original_error: Exception = None):
        if original_error:
            message = f"{self.DEFAULT_MESSAGE} Original error: {original_error}"
        else:
            message = self.DEFAULT_MESSAGE
        super().__init__(message)


class LoggerWriteError(IOError, LoggerError):
    """
    Raised when logger fails to write the log file

    This could be due to several conditions:
        Permission
        Full disk
        Other file system issues
    """

    pass
