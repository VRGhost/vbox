from vbox import pyVb

from . import vm, general

class VirtualBox(object):
    """host-wide functionality."""

    def __init__(self):
        self.vb = pyVb.VirtualBox()

    def vms(self):
        for pyVm in self.vb.vms.list():
            yield vm.VM(
                general.DetachedGeneral(
                    name=pyVm.name,
                    osType=pyVm.osType,
                )
            )