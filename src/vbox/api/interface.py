from . import (
    dvd,
    exceptions,
    floppy,
    hdd,
    host,
    network,
    vm,
    meta,
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
        self.networking = network.Library(self.source.networking, self)
        self._globalExtraData = meta.Meta(self.source.extraData)

    def extraData(self, name):
        """Return extra data object.

        This object provides dictionary interface and is stored in the global scope of
        vboxManage.

        All changes to this object are serialised and stored in the virtualbox.
        """
        try:
            return self._globalExtraData[name]
        except KeyError:
            self._globalExtraData[name] = {}
            return self._globalExtraData[name]
