from .. import base
from vbox import util

ElementGroup = base.ElementGroup
VirtualBoxEntityType = base.VirtualBoxEntityType
VirtualBoxObject = base.VirtualBoxObject

class EnabledDisabled(util.Switch):

    trueVals = ("Enabled", )
    falseVals = ("Disabled", )

class UpDown(util.Switch):
    trueVals = ("Up", )
    falseVals = ("Down", )

class ColonSeparatedMac(util.String):

    def fromCli(self, val):
        rv = val.replace(':', '')
        assert len(rv) == 12
        return rv

    def toCli(self, val):
        assert len(val) == 12
        out = []
        while val:
            out.append(val[:2])
            val = val[2:]
        return ':'.join(out)