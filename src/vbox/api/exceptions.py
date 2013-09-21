class ApiError(Exception):
    pass

class ControllerError(ApiError):
    pass

class ControllerFull(ControllerError):
    pass

class SlotBusy(ControllerError):
    pass

class MissingFile(ApiError):
    pass