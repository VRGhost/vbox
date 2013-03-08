"""manage list command."""

import re

from . import subCmd, util

class List(subCmd.Base):

    PlainOutputs = (
        "systemproperties", "hostinfo")
    GroupOutputs = (
        "ostypes", "runningvms", "hostdvds",
        "hostfloppies", "bridgedifs", "hostonlyifs",
        "dhcpservers",
        )

    _all = None
    def all(self):
        if not self._all:
            outp = self.checkOutput([], rc=1)
            outp = "".join(line.strip() for line in outp.splitlines())
            match = re.search(r"(\w+(?:\|\w+)+)", outp)
            self._all = tuple(match.group(1).split('|'))
        return self._all

    vms = lambda s: s._vmList("vms")

    def _vmList(self, cmd):
        txt = self.checkOutput([cmd])
        return dict((el[1], el[2]) for el in util.iterMatches(r"^\s*(['\"])(.*?)\1\s+{(.*?)}\s*$", txt))

    def _groupOutput(self, name):
        return tuple(util.iterParamGroups(self.checkOutput([name])))

    def _plainOutput(self, name):
        return util.parseParams(self.checkOutput([name]))

    for name in PlainOutputs:
        locals()[name] = (lambda name: (lambda s: s._plainOutput(name)))(name)
    for name in GroupOutputs:
        locals()[name] = (lambda name: (lambda s: s._groupOutput(name)))(name)
    del name