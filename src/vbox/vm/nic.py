"""Network interface card support."""
import re

from . import base
from . import vmProps as props

class NIC(base.VirtualMachinePart):
    

    hwType = property(lambda s: s.getProp("nictype"))
    speed = property(lambda s: int(s.getProp("nicspeed")))

    def _getInfo(self):
        par = self.vm.info
        if not par:
            return None

        out = {}
        for name in (
            "nic", "nictype", "nicspeed", "cableconnected",
            "macaddress",
        ):
            name = self.getPropName(name)
            out[name] = par.get(name)

        print out
        return out

    def getPropName(self, prefix):
        return "{}{}".format(prefix, self.idx)

    def type():
        doc = "The type property."
        def fget(self):
            rv = self.getProp("nic")
            if rv == "none":
                rv = None
            return rv
        def fset(self, value):
            if value is None:
                value = "none"
            self.setProp("nic", value)
            #self.control({"nic": value}, quiet=True)
        def fdel(self):
            self.type = None
        return locals()
    type = property(**type())

    cableConnected = props.Switch("cableconnected", control="setlinkstate")
    mac = props.String("macaddress")

class NicGroup(base.PartGroup):
    
    parentRe = re.compile(r"^nic(\d+)$")
    childCls = NIC