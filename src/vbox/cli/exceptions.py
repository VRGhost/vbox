from .. import exceptions

class CalledProcessError(exceptions.BaseException):
    """Emulates subprocess exception interface."""

    def __init__(self, cmd, rc, output):
        super(CalledProcessError, self).__init__(
            "Error calling {!r} (rc={!r}). Output:\n\n{}".format(cmd, rc, output[-500:])
        )
        self.returncode = rc
        self.cmd = tuple(cmd)
        self.output = output

class ParsedVboxError(CalledProcessError):

    def __init__(self, cmd, rc, output, errorName, errorCode, message):
        super(CalledProcessError, self).__init__(
            "Error calling {!r}: {!r} (0x{:X}):: {}".format(cmd, errorName, errorCode, message)
        )
        self.returncode = rc
        self.cmd = tuple(cmd)
        self.output = output
        self.errorName = errorName
        self.errorCode = errorCode
        self.msg = message