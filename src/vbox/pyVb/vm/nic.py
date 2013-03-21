"""Network interface card support."""
import re

from .. import util as props

from . import base, util

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
            "macaddress", "bridgeadapter", "hostonlyadapter"
        ):
            name = self.getPropName(name)
            out[name] = par.get(name)

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
            self.control({"nic": value}, quiet=True)
            # Set the attached network adapter if required
            if not self.networkAdapter:
                if value == "hostonly":
                    lib = self.vb.net.hostOnlyInterfaces
                elif value == "bridgeadapter":
                    lib = self.vb.net.bridgedInterfaces
                else:
                    lib = None

                if lib:
                    for el in lib.list():
                        adapter = el
                        break
                    else:
                        adapter = None

                if adapter:
                    self.networkAdapter = adapter
        def fdel(self):
            self.type = None
        return locals()
    type = property(**type())

    cableConnected = props.Switch(
        "cableconnected", extraCb=util.controlCb("setlinkstate"))
    mac = props.String("macaddress")

    def networkAdapter():
        doc = """The networkAdapter property.

        Controls acutal host-level NIC attached to the VM nic
        """
        def _propName(typ):
            if typ == "hostonly":
                rv = "hostonlyadapter"
            elif typ == "bridged":
                rv = "bridgeadapter"
            else:
                # Not applicable
                rv = None
            return rv

        def fget(self):
            prop = _propName(self.type)
            if not prop:
                return None
            adapterName = self.getProp(prop)
            if adapterName:
                rv = self.vb.net.find(adapterName)
                assert rv
            else:
                rv = None 
            return rv
        def fset(self, value):
            prop = _propName(self.type)
            if not prop:
                return None

            if not value:
                value = None
            else:
                try:
                    value = value.name
                except AttributeError:
                    value = str(value)
            self.setProp(prop, value)
        return {"fget": fget, "fset": fset}
    networkAdapter = property(**networkAdapter())

class NicGroup(base.PartGroup):
    
    parentRe = re.compile(r"^nic(\d+)$")
    childCls = NIC