from . import (
    vm,
    hdd,
)

class VirtualBox(object):

    def __init__(self, cli):
        super(VirtualBox, self).__init__()
        self.cli = cli
        self.vms = vm.Library(self)
        self.hdds = hdd.Library(self)