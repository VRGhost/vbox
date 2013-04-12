from . import (
    subCmd,
    util,
)


class GuestProperty(subCmd.PlainCall):

    changesVmState = False

    def enumerate(self, id):
        return self("enumerate", id)


class GuestControl(subCmd.PlainCall):

    changesVmState = False

    def copyto(self, id, src, dst, username, password="", follow=False, recursive=False):
        cmd = [
            id, "copyto", src, dst,
            "--username", username,
            "--password", password,
            "--verbose",
        ]
        if follow:
            cmd.append("--follow")
        if recursive:
            cmd.append("--recursive")
        return self(*cmd)