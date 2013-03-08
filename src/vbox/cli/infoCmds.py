"""Information commands."""

from . import (
    subCmd,
    util,
)

class ShowHdInfo(subCmd.PlainCall):

    def getRcHandlers(self):
        return {
            1: lambda txt: None
        }


class ShowVmInfo(subCmd.PlainCall):

    def getRcHandlers(self):
        return {
            1: lambda txt: None
        }

    def __call__(self, id):
        return super(ShowVmInfo, self).__call__("--details", "--machinereadable", id)