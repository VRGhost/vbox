from . import (
    hdd,
    host,
    vm,
)

class VirtualBox(object):

    def __init__(self, source):
        super(VirtualBox, self).__init__()
        self.source = source

        self.host = host.Host(self.source.host, self)
        self.vms = vm.Library(self.source.vms, self)
        self.hdds = hdd.Library(self.source.hdds, self)