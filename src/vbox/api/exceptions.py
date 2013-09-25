from .. import exceptions

class ApiError(exceptions.BaseException):
    pass

class ControllerError(ApiError):
    pass

class ControllerFull(ControllerError):
    pass

class SlotBusy(ControllerError):
    pass

class MissingFile(ApiError):
    pass

class VmNotFound(ApiError):
    pass

class VmAlreadyExists(ApiError):
    pass