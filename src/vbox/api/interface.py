from . import (
    vm,
    hdd,
)

class VirtualBox(object):

    def __init__(self, source):
        super(VirtualBox, self).__init__()
        self.source = source

        self.vms = vm.Library(self.source.vms, self)
        self.hdds = hdd.Library(self.source.hdds, self)