"""Network interface card support."""
import re

from . import base
from . import vmProps as props

class NIC(base.VirtualMachinePart):
    

    hwType = property(lambda s: s.getProp("type"))
    speed = property(lambda s: int(s.getProp("speed")))

    def _getInfo(self):
        par = self.vm.info
        if not par:
            return None

        out = {}
        for name in ("nic", "nictype", "nicspeed"):
            out[name] = par.get(self._propName(name))

        print [el for el in par.keys() if "mac" in el.lower()]
        out["cableconnected"] = par.get("cableconnected{}".format(self.idx))
        print out
        return out

    def _propName(self, prefix):
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
            self.vm.setProp(self._propName("nic"), value)
        def fdel(self):
            self.type = None
        return locals()
    type = property(**type())

    def cableConnected():
        doc = "The cableConnected property."
        def fget(self):
            name = self._propName("cableconnected")
            return (self.getProp(name) == "on")
        def fset(self, value):
            val = "on" if value else "off"
            name = self._propName("cableconnected")
            self.vm.setProp(name, val)
        def fdel(self):
            del self._cableConnected
        return locals()
    cableConnected = property(**cableConnected())

class NicGroup(base.PartGroup):
    
    parentRe = re.compile(r"^nic(\d+)$")
    childCls = NIC