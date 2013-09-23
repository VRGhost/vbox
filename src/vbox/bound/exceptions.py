from .. import exceptions

class BoundError(exceptions.BaseException):
    pass

class FileAlreadyExists(BoundError):
    pass

class VmNotFound(BoundError):
    pass