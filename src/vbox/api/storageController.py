import collections
import re

from . import (
    base,
    props,
)

STORAGE_CONTROLLER_NAME_RE = re.compile("^storagecontrollername(\d+)$")
def cls_name_gen(fld, idx):
    return "storagecontroller{}{}".format(fld, idx)

class MountedMedium(base.SubEntity):

    def __init__(self, controller, medium, slot):
        super(MountedMedium, self).__init__(controller)
        self.controller = controller
        self.medium = medium
        self.slot = slot

    @props.SourceProperty
    def isEjectable(self):
        """VM guest won't be able to eject this dvd disk if this returns 'True'.

        Useful for liveCDs.
        """
        myKey = self.controller._slotToKey(self.slot)
        myIdx = self.source.info.index(myKey)
        (nextKey, nextVal) = self.source.info.getByIndex(myIdx + 1)
        if nextKey == "{}-IsEjected".format(self.controller.name):
            assert nextVal in ("on", "off")
            rv = (nextVal == "off")
        else:
            rv = None
        return rv

    def __repr__(self):
        return "<{} {!r} @ {}>".format(self.__class__.__name__, self.medium, self.slot)

class Controller(base.SubEntity):

    maxPortCount = props.SourceInt(lambda s: s.source.info.get(cls_name_gen("maxportcount", s.idx)))
    portCount = props.SourceInt(lambda s: s.source.info.get(cls_name_gen("portcount", s.idx)))
    instance = props.SourceInt(lambda s: s.source.info.get(cls_name_gen("instance", s.idx)))
    hwType = props.SourceStr(lambda s: s.source.info.get(cls_name_gen("type", s.idx)))
    bootable = props.OnOff(lambda s: s.source.info.get(cls_name_gen("bootable", s.idx)))
    
    def __init__(self, parent, name):
        super(Controller, self).__init__(parent)
        self.name = name

    @props.SourceInt
    def idx(self):
        for (name, value) in self.source.info.iteritems():
            match = STORAGE_CONTROLLER_NAME_RE.match(name)
            if match and (value == self.name):
                idx = match.group(1)
                return int(idx)

    @props.SourceProperty
    def slots(self):
        prefix = "{}-".format(self.name)
        data = collections.defaultdict(dict)
        prevEl = None
        for (name, value) in self.source.info.iteritems():
            if name.startswith(prefix):
                val = name[len(prefix):]
                params = val.split('-')
                parLen = len(params)

                if parLen == 1:
                    assert prevEl
                    target = prevEl
                else:
                    assert parLen in (2, 3)
                    (base, subBase) = params[-2:]
                    slot = (int(base), int(subBase))
                    target = data[slot]
                    target["slot"] = slot

                if parLen in (1, 3):
                    fieldName = params[0]
                else:
                    fieldName = "medium"

                target[fieldName] = value
                prevEl = target


        out = {}
        for (slot, value) in data.iteritems():
            if value["medium"] == "none":
                outVal = None
            else:
                outVal = self._mkMedium(value)
            out[slot] = outVal

        return out

    @props.SourceProperty
    def type(self):
        """Return controller type: sata/ata/etc."""
        hwType = self.hwType.upper()
        if hwType in ("PIIX3", "PIIX4", "ICH6"):
            rv = "ide"
        elif hwType in ("INTELAHCI", ):
            rv = "sata"
        elif hwType in ("LISLOGIC", "BUSLOGIC"):
            rv = "scsi"
        elif hwType in ("LISLOGIC SAS", ):
            rv = "sas"
        elif hwType in ("I82078", ):
            rv = "floppy"
        else:
            raise NotImplementedError(hwType)
        return rv

    def attach(self, object, bootable=None):
        slot = self.findEmptySlot(ensureMaster=bootable)
        if not slot:
            raise self.exceptions.ControllerFull()
        self.attachTo(slot, object)

    def attachTo(self, slot, object):
        if self.slots[slot]:
            raise self.exceptions.SlotBusy(slot)

        if object is None:
            kw = {"medium": "none"}
        else:
            kw = object.getStorageAttachKwargs()

        kw.update({
            "storagectl": self.name,
            "port": slot[0],
            "device": slot[1],
        })
        self.source.storageAttach(**kw)

    def getMedia(self, slot):
        rv = self.slots[slot]
        if rv:
            rv = rv.medium
        return rv

    def findSlotOf(self, obj):
        if not obj:
            return self.findEmptySlot()

        for (slot, val) in self.slots.iteritems():
            if not val:
                continue

            if obj == val.medium:
                return slot
        return None

    def findEmptySlot(self, ensureMaster=True):
        for (slot, value) in self.slots.iteritems():
            if not value:
                if ensureMaster and slot[1] != 0:
                    continue
                return slot
        else:
            return None

    def _mkMedium(self, data):
        """Find and retunrn medium object described.

        This method is used in the `storageController.Controler` implementation
        to map the VM medium desctiptions to Python objects.
        """
        rv = None
        medium = data["medium"]
        interface = self.interface

        if medium == "emptydrive":
            if self.type == "floppy":
                rv = interface.floppies.empty
            else:
                rv = interface.dvds.empty
        else:
            try:
                hdd = self.interface.hdds.fromFile(data["medium"])
            except self.exceptions.MissingFile:
                pass
            else:
                if hdd.accessible:
                    rv = hdd
        
        if not rv:
            rv = interface.floppies.fromFile(data["medium"])

        return MountedMedium(self, rv, data["slot"])

    def _slotToKey(self, slot):
        return "{}-{}".format(self.name, '-'.join(str(el) for el in slot))

    def __repr__(self):
        return "<{}.{} {!r}>".format(self.__module__, self.__class__.__name__, self.name)

def _typeAccessorProp(typ):
    def _wrapper(self):
        rv = self.find(typ)
        if rv:
            rv = rv[0]
        else:
            rv = None
        return rv
    _wrapper.__name__ = "_{}_accessor".format(typ)
    return props.SourceProperty(_wrapper)

class Library(base.SubEntity):
    """Storage controller library."""
    
    # The below ide/sata/etc accessors take advantage of the fact that virtualbox does not support
    # More than one controller of each type per VM.
    ide = _typeAccessorProp("ide")
    sata = _typeAccessorProp("sata")
    floppy = _typeAccessorProp("floppy")
    scsi = _typeAccessorProp("scsi")


    @props.SourceProperty
    def all(self):
        matcher = STORAGE_CONTROLLER_NAME_RE
        names = []

        for (key, value) in self.source.info.iteritems():
            match = matcher.match(key)
            if match:
                names.append(value)

        return tuple(Controller(self, name) for name in names)

    def create(self, type, name=None, hwType=None, sataPortCount=None, hostIoCache=None, bootable=True):
        if not name:
            usedNames = frozenset(el.name for el in self.all)
            idx = 1
            while "{}_{}".format(type, idx) in usedNames:
                idx += 1
            name = "{}_{}".format(type, idx)

        callKw = {"name": name, "add": type}
        if hwType:
            callKw["controller"] = hwType
        if (type == "sata") and (sataPortCount is not None):
            callKw["sataportcount"] = sataPortCount
        if hostIoCache is not None:
            callKw["hostIoCache"] = "on" if hostIoCache else "off"
        if bootable is not None:
            callKw["bootable"] = "on" if bootable else "off"
        self.source.storageCtl(**callKw)

    def ensureExist(self, type, name=None, createKw=None):
        if not self.find(type, name):
            if not createKw:
                createKw = {}
            self.create(type, name=name, **createKw)

    def find(self, type, name=None):
        if name:
            matchFn = lambda cnt: (cnt.type == type) and (cnt.name == name)
        else:
            matchFn = lambda cnt: cnt.type == type
        return tuple(el for el in self.all if matchFn(el))