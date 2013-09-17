from .. import exceptions

class CmdError(exceptions.BaseException):
    """Base class for command-line exceptions."""

    def __str__(self):
        return "{!r} failed with rc={} and output:\n=====\n{}\n========".format(
            self.returncode, self.cmd, self.output)