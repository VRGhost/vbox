"""VM storage controller."""
from collections import OrderedDict, defaultdict
import re

from . import base

class StorageController(base.VirtualMachinePart):

    name = property(lambda s: s.getProp("name"))
    hwType = property(lambda s: s.getProp("type"))
    instance = property(lambda s: s.getProp("instance"))
    maxPortCount = property(lambda s: s.getProp("maxportcount", int))
    portCount = property(lambda s: s.getProp("portcount", int))
    bootable = property(lambda s: s.getProp("bootable") == "on")

    def destroy(self):
        self.vb.cli.manage.storagectl(self.vm.id, self.name, remove=True)

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

    def attach(self, what, type=None, slot=None, ensureBootable=False):
        if isinstance(what, basestring):
            medium = what
        else:
            medium = what.getVmAttachMedium()
        if not type:
            type = what.getVmAttachType()
        if not slot:
            if ensureBootable:
                slot = self.findEmptySlot(ensureMaster=True)
            else:
                slot = self.findEmptySlot()
            if not slot:
                raise Exception("No empty slots found.")
        self.vb.cli.manage.storageattach(self.vm.id, self.name,
            port=slot[0], device=slot[1], type=type,
            medium=medium
        )
        return slot

    def findEmptySlot(self, ensureMaster=False):
        for slot in self.iterSlots():
            if not self.getMedia(slot):
                if ensureMaster and (port != 0):
                    continue
                    
                return slot

    def findSlotOf(self, image):
        for (addr, media) in self.iterMedia():
            if media == image:
                return addr
        return None

    def getMedia(self, slot):
        for (addr, value) in self.iterMediaInfo():
            if addr == slot:
                return self._convertMediaVal(value)
        return None

    def iterSlots(self):
        return (el[0] for el in self.iterMediaInfo())

    def iterMedia(self):
        for (name, value) in self.iterMediaInfo():
            pyObject = self._convertMediaVal(value)
            if pyObject is not None:
                yield (name, pyObject)

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

        if self.type == "floppy":
            lib = self.vb.floppies
        else:
            lib = self.vb.dvds

        if name == "emptydrive":
            return lib.empty
        else:
            return lib.get(name)

        raise Exception("Unknown media value {!r}".format(val))

    def iterMediaInfo(self):
        prefix = "self-"
        lastDevice = None
        out = defaultdict(dict)
        for (name, value) in self.info.iteritems():
            if not name.startswith(prefix):
                continue
            parts = name.rsplit('-', 3)
            assert parts[0] == "self"
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

        keys = out.keys()
        keys.sort()
        for key in keys:
            yield (key, out[key])

    def _getInfo(self):
        par = self.vm.info
        if not par:
            return None

        ids = str(self._initId)
        prefix = "storagecontroller"
        out = OrderedDict()
        for (name, value) in par.iteritems():
            if not(name.startswith(prefix) and name.endswith(ids)):
                continue
            # else
            localName = name[len(prefix):-len(ids)]
            out[localName] = value

        if not out:
            return None


        name = out["name"]
        namedprefix = "{}-".format(name)
        for (name, value) in par.iteritems():
            if not name.startswith(namedprefix):
                continue
            localName = "self-{}".format(name[len(namedprefix):])
            out[localName] = value
        
        return out

class ControllerGroup(base.PartGroup):

    parentRe = re.compile(r"^storagecontrollername(\d+)$")
    childCls = StorageController

