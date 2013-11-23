import re

from .. import (
    base,
    util,
)

class HostOnlyIf(base.SubCommand):

    formatter = util.Formatter(
        all=("action", "target", "dhcp", "ip", "netmask", "ipv6", "netmasklengthv6"),
        positional=("{action}", "{target}"),
        flags=("dhcp", ),
        mandatory=("action", ),
    )

    createOkRe = re.compile(r"^Interface '(\w+)' was successfully created$", re.M | re.I)
    def create(self):
        txt = self(action="create")
        match = self.createOkRe.search(txt)
        if match:
            return match.group(1)
        else:
            raise self.exceptions.UnexpectedOutput("No interface name found", txt)

    def remove(self, name):
        return self(action="remove", target=name)