import vbox.base

from . import (
    dvd,
    exceptions,
    extraData,
    floppy,
    hdd,
    host,
    network,
    usb,
    vm,
)

class VirtualBox(vbox.base.CacheChain):

    exceptions = exceptions

    def __init__(self, cli):
        super(VirtualBox, self).__init__()
        self.cli = cli
        self._libraris = _libs = []

        self.host = host.Host(self)
        self.vms = vm.Library(self)
        self.hdds = hdd.Library(self)
        self.dvds = dvd.Library(self)
        self.floppies = floppy.Library(self)
        self.networking = network.Library(self)
        self.usb = usb.Library(self)
        self.extraData = extraData.ExtraData(self.cli, "global")