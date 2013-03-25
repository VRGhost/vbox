from vbox import pyVb

from . import (
    base,
    display,
    network,
    system,
)

from extraData import ExtraData

class VM(base.Base):

    kwargName = "vm"
    initOrder = ("general", )
    expectedKwargs = {
        "general": 1,
        "system": (0, 1),
        "display": (0, 1),
        "storage": 1,
        "network": (0, 1),
    }
    defaultKwargs = {
        "system": system.System,
        "display": display.Display,
        "network": network.Network,
    }
    pyVb = pyVm = None

    start = base.pyVmProp("start")
    wait = base.pyVmProp("wait")
    powerOff = base.pyVmProp("powerOff")
    destroy = base.pyVmProp("destroy")

    meta = None

    def general():
        doc = "The 'general' property. It updates actual pyVb vm object bound to this API entity"
        def fget(self):
            return self._general
        def fset(self, value):
            self._general = value
            vm = self.pyVb.vms.find(value.name)
            if vm is None:
                vm = self.pyVb.vms.create(
                    autoname=False,
                    name=value.name,
                    ostype=value.osType or None,
                    register=True,
                )
            self.pyVm = vm
        return locals()
    general = property(**general())

    def __init__(self, *args, **kwargs):
        # The `pyVb` object has to be declared prior the __init__ call,
        # as __init__ relies on the ability to access virtualbox object.
        #
        # However, I do beleive that initialising object in such manner is a bad style
        # and should be avoided whenever possible. Thus, I will perform post-super
        # initialisation whenever possible.
        self.pyVb = pyVb.VirtualBox()
        super(VM, self).__init__(*args, **kwargs)

        self.meta = ExtraData(self)
