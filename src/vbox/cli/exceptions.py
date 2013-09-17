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