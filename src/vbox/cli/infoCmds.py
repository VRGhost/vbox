"""Information commands."""

from . import (
    subCmd,
    util,
)

class ShowHdInfo(subCmd.PlainCall):

    changesVmState = False

    def getRcHandlers(self):
        return {
            1: lambda cmd, txt: None
        }


class ShowVmInfo(subCmd.PlainCall):

    changesVmState = False

    def getRcHandlers(self):
        return {
            1: lambda cmd, txt: None
        }

    def __call__(self, id):
        return super(ShowVmInfo, self).__call__("--details", "--machinereadable", id)


class GuestProperty(subCmd.PlainCall):

    changesVmState = False

    def enumerate(self, id):
        return self("enumerate", id)