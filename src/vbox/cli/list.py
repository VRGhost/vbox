"""manage list command."""

import re

from . import subCmd, util

class List(subCmd.Base):

    changesVmState = False
    PlainOutputs = (
        "systemproperties", "hostinfo")
    GroupOutputs = (
        "runningvms", "hostdvds",
        "hostfloppies", "bridgedifs", "hostonlyifs",
        "dhcpservers", "hdds", "dvds", "floppies", 
        )

    _all = None
    def all(self):
        if not self._all:
            (rc, cmd, outp) = self.call([])
            assert rc == 1, cmd
            outp = "".join(line.strip() for line in outp.splitlines())
            match = re.search(r"(\w+(?:\|\w+)+)", outp)
            self._all = tuple(match.group(1).split('|'))
        return self._all

    vms = lambda s: s._vmList("vms")

    def ostypes(self):
        """Ostypes never change and can be permamently cached."""
        try:
            return self.__ostypeCache
        except AttributeError:
            rv = util.iterParamGroups(self.checkOutput(["ostypes"]))
            rv = tuple(rv)
            self.__ostypeCache = rv
            return rv

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