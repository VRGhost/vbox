from . import (
    dvd,
    exceptions,
    floppy,
    hdd,
    host,
    vm,
)

class VirtualBox(object):

    exceptions = exceptions

    def __init__(self, source):
        super(VirtualBox, self).__init__()
        self.source = source

        self.host = host.Host(self.source.host, self)
        self.vms = vm.Library(self.source.vms, self)
        self.hdds = hdd.Library(self.source.hdds, self)
        self.dvds = dvd.Library(self.source.dvds, self)
        self.floppies = floppy.Library(self.source.floppies, self)
