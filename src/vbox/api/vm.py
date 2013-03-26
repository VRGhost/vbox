from vbox import pyVb

from . import (
    base,
    display,
    general,
    network,
    storage,
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
        "storage": (0, 1),
        "network": (0, 1),
    }
    defaultKwargs = {
        "system": system.System,
        "display": display.Display,
        "network": network.Network,
        "storage": storage.Storage,
    }
    pyVb = pyVm = None

    start = base.pyVmProp("start")
    wait = base.pyVmProp("wait")
    powerOff = base.pyVmProp("powerOff")
    suspend = base.pyVmProp("suspend")
    destroy = base.pyVmProp("destroy")

    meta = None
    vm = property(lambda s: s)

    def general():
        doc = "The 'general' property. It updates actual pyVb vm object bound to this API entity"
        def fget(self):
            return self._general
        def fset(self, value):
            vm = self.pyVb.vms.find(value.name)
            if vm is None:
                extraKw = {}
                if value.directory:
                    extraKw["basefolder"] = value.directory

                vm = self.pyVb.vms.create(
                    autoname=False,
                    name=value.name,
                    ostype=value.osType or None,
                    register=True,
                    groups=general.groupsToCli(value.groups),
                    **extraKw
                )
            self.pyVm = vm
            self._general = general.InteractiveGeneral(value)
            self._registerAsParent(self._general)
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
