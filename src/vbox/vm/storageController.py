"""VM storage controller."""

from . import base

class StorageController(base.VirtualMachinePart):

    name = property(lambda s: s.getProp("name"))
    hwType = property(lambda s: s.getProp("type"))
    instance = property(lambda s: s.getProp("instance"))
    maxPortCount = property(lambda s: s.getProp("maxportcount", int))
    portCount = property(lambda s: s.getProp("portcount", int))
    bootable = property(lambda s: s.getProp("bootable") == "on")

    def destroy(self):
        self.vb.cli.manage.storagectl(self.vm.UUID, self.name, remove=True)
        self.refresh()

    @property
    def type(self):
        hw = self.hwType
        if hw in ("PIIX3", "PIIX4", "ICH6"):
            return "ide"
        elif hw in ("BusLogic", "LsiLogic"):
            return "scsi"
        elif hw in ("I82078", ):
            return "floppy"
        elif hw in ("IntelAhci", ):
            return "sata"
        else:
            raise Exception("Unknown hw type {!r}".format(hw))

    def getProp(self, name, type=None):
        print self.info
        rv = self.vm.getProp("storagecontroller{}{}".format(name, self.idx))
        if type:
            rv = type(rv)
        return rv

    def attach(self, what, type=None, slot=None):
        if isinstance(what, basestring):
            medium = what
        else:
            medium = what.getVmAttachMedium()
        if not type:
            type = what.getVmAttachType()
        if not slot:
            slot = self.findEmptySlot()
            if not slot:
                raise Exception("No empty slots found.")
        self.vb.cli.manage.storageattach(self.vm.UUID, storagectl=self.name,
            port=slot[0], device=slot[1], type=type,
            medium=medium
        )
        self.refresh()

    def findEmptySlot(self):
        for (dev, port) in self.iterSlots():
            if not self.getMedia(dev, port):
                return (dev, port)

    def findSlotOf(self, image):
        for (addr, media) in self.iterMedia():
            if media == image:
                return addr
        return None

    def getMedia(self, device, port):
        target = (device, port)
        for (addr, value) in self.iterMediaInfo():
            if addr == target:
                return self._convertMediaVal(value)
        return None

    def iterSlots(self):
        return (el[0] for el in self.iterMediaInfo())

    def iterMedia(self):
        for (name, value) in self.iterMediaInfo():
            yield (name, self._convertMediaVal(value))

    def _convertMediaVal(self, val):
        if val["name"] == "none":
            return None
        
        # Try to search for object with given UUID
        uuid = val.get("ImageUUID")
        if uuid:
            rv = self.vb.find(uuid)
            if rv:
                return rv

        name = val.get("name")
        if name == "emptydrive":
            if self.type == "floppy":
                return self.vb.mediums.floppy.empty
            else:
                return self.vb.mediums.dvd.empty
        else:
            raise NotImplementedError(name)

        raise Exception("Unknown media value {!r}".format(val))

    def iterMediaInfo(self):
        prefix = "{}-".format(self.name)
        lastDevice = None
        out = defaultdict(dict)
        for (name, value) in self.vm.info.iteritems():
            if not name.startswith(prefix):
                continue
            parts = name.rsplit('-', 3)
            assert parts[0] == self.name
            parts.pop(0)

            if len(parts) > 1:
                # device connection id present
                device = tuple(int(el) for el in parts[-2:])
                parts = parts[:-2]
            else:
                # Device connection id not present, assuming to be same are previous
                device = lastDevice

            if parts:
                assert len(parts) == 1, parts
                infix = parts[0]
            else:
                infix = "name"

            out[device][infix] = value
            lastDevice = device

        return out.iteritems()