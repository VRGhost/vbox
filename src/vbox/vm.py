"""VM class."""
import re
from collections import defaultdict

from . import base
from .cli import util

class VM(base.VirtualBoxEntity):
    
    name = property(lambda s: s.getProp("name"))
    idProps = base.VirtualBoxEntity.idProps + ("name", )

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self._controllers = []

    def _getInfo(self):
        txt =  self.vb.cli.manage.showvminfo(self._initId)
        if txt:
            return dict(util.parseMachineReadableFmt(txt))
        else:
            return None

    def destroy(self, complete=True):
        self.vb.cli.manage.unregistervm(name=self.getId(), delete=complete)
        super(VM, self).destroy()

    def unregister(self, delete=True):
        return self.destroy(complete=delete)


    def findControllers(self, type):
        return (el for el in self._controllers if el.type == type)

    def getControoler(self, name):
        # Touch 'info' property to ensure that controller registy is up to date
        self.info
        for el in self._controllers:
            if el.name == name:
                return el

    def createController(self, name, type, **kwargs):
        assert not self.getControoler(name)
        self.vb.cli.manage.storagectl(self.UUID, name, add=type)
        del self.info
        obj = self.getControoler(name)
        assert obj.type == type
        return obj

    @property
    def ide(self):
        typ = "ide"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    @property
    def sata(self):
        typ = "sata"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    @property
    def floppy(self):
        typ = "floppy"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    def onInfoUpdate(self):
        nameFields = [el for el in self.info.keys() if el.startswith("storagecontrollername")]
        if nameFields:
            idRe = re.compile(r"^storagecontrollername(\d+)$")
            ids = []
            for str in nameFields:
                match = idRe.match(str)
                ids.append(int(match.group(1)))

            destroyed = []
            for contr in self._controllers:
                if contr.idx in ids:
                    ids.remove(contr.idx)
                else:
                    # Controller is no longer part of VM
                    destroyed.append(contr)
            for el in destroyed:
                el.onDestroyed()
            for idx in ids:
                # New controllers
                self._controllers.append(StorageController(self, idx))

    def onStorageDestroyed(self, obj):
        self.onStorageChanged(obj)
        self._controllers.remove(obj)

    def onStorageChanged(self, obj):
        del self.info

class StorageController(object):

    name = property(lambda s: s.getProp("name"))
    hwType = property(lambda s: s.getProp("type"))
    instance = property(lambda s: s.getProp("instance"))
    maxPortCount = property(lambda s: s.getProp("maxportcount", int))
    portCount = property(lambda s: s.getProp("portcount", int))
    bootable = property(lambda s: s.getProp("bootable") == "on")

    def __init__(self, vm, idx):
        self.vm = vm
        self.vb = vm.vb
        self.idx = idx

    def destroy(self):
        self.vb.cli.manage.storagectl(self.vm.UUID, self.name, remove=True)
        self.onDestroyed()

    def onDestroyed(self):
        self.vm.onStorageDestroyed(self)

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

    def findEmptySlot(self):
        for (dev, port) in self.iterSlots():
            if not self.getMedia(dev, port):
                return (dev, port)

    def getMedia(self, device, port):
        val = self.vm.getProp("{}-{}-{}".format(self.name, device, port))
        if val == "none":
            return None
        else:
            raise Exception("Unknown media value {!r}".format(vla))

    def iterSlots(self):
        prefix = "{}-".format(self.name)
        for name in self.vm.info.keys():
            if not name.startswith(prefix):
                continue
            (pref, device, port) = name.split("-", 2)
            yield (int(device), int(port))