class BaseException(Exception):
    """Base class for all exceptions in the project."""

class VirtualBoxNotFound(BaseException):
    """Virtualbox executable not found."""