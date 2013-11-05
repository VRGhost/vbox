"""Storage-related interfaces."""

import os
from . import base

class Bus(base.SubConfigEntity):

    busType = None

    def parentObjToMyObj(self, controller):
        rv = controller.find(self.busType)
        if not rv:
            raise self.exceptions.ConfigError("Unable to find {!r} in {!r}".format(self.busType, controller))
        return tuple(rv)[0]

    def dataToMedia(self, data, type):
        if data:
            handler = getattr(self.api, type)
            rv = handler.create(**data)
        else:
            rv = None
        return rv


class FloppyBus(Bus):

    busType = "floppy"

    def setup(self, obj, data):
        obj = self.parentObjToMyObj(obj)

        for el in data:
            target = el.pop("target", None)
            if target:
                img = self.api.floppies.fromFile(target)
            else:
                img = self.api.floppies.empty


            if obj.findSlotOf(img) is None:
                obj.attach(img, el.get("bootable", None))

    def ensure(self, obj, data):
        raise NotImplementedError

class SataOrIdeBus(Bus):

    def setup(self, obj, data):
        obj = self.parentObjToMyObj(obj)
        for el in data:
            if not self._imgMatch(obj, el):
                obj.attach(self._mkImg(el), el.get("bootable", None))

    def ensure(self, obj, data):
        obj = self.parentObjToMyObj(obj)
        for el in data:
            if not self._imgMatch(obj, el):
                raise self.exceptions.EnsureMismatch(obj, obj.type, el, "<unknown>")

    def _imgMatch(self, cntrl, data):
        if "target" in data:
            return (cntrl.findSlotOf(self._mkImg(data)) is not None)

        matchFuncs = []
        if "size" in data:
            matchFuncs.append(lambda medium: medium.maxSize == data["size"])
        if "type" in data:
            matchFuncs.append(lambda medium: medium.getStorageAttachKwargs()["type"] == data["type"])

        if not matchFuncs:
            raise NotImplementedError(data)


        for el in cntrl.slots.values():
            if not el:
                continue
            medium = el.medium
            if all(fn(medium) for fn in matchFuncs):
                return True
        return False


    def _mkImg(self, data):
        typ = data.get("type", "hdd")
        if typ == "hdd":
            kw = {"size": data["size"]}
            path = data.get("filename")
            if path:
                (root, fname) = os.path.split(path)
                fname = os.path.splitext(fname)[0]
                kw.update({
                    "targetDir": root,
                    "basename": fname,
                })
            rv = self.api.hdds.create(**kw)
        elif typ == "dvddrive":
            target = data.get("target")
            if not target:
                rv = self.api.dvds.empty
            elif target == "guest_additions":
                rv = self.api.dvds.guestAdditions
            elif os.path.exists(target):
                rv = self.api.dvds.fromFile(target)
            else:
                raise NotImplementedError(target)
        else:
            raise NotImplementedError(typ)
        return rv


class SataBus(SataOrIdeBus):
    busType = "sata"

class IdeBus(SataOrIdeBus):
    busType = "ide"

class Controller(base.SubConfigEntity):

    customHandlers = ("ide", "sata", "floppy")

    def setup_floppy(self, obj, data):
        self._act("floppy", obj, data, mode="setup")

    def ensure_floppy(self, obj, data):
        self._act("floppy", obj, data, mode="ensure")

    def setup_ide(self, obj, data):
        self._act("ide", obj, data, mode="setup")

    def ensure_ide(self, obj, data):
        self._act("ide", obj, data, mode="ensure")

    def setup_sata(self, obj, data):
        self._act("sata", obj, data, mode="setup")

    def ensure_sata(self, obj, data):
        self._act("sata", obj, data, mode="ensure")

    def _act(self, type, obj, data, mode):
        createKw = data.copy()
        if "targets" in createKw:
            targets = createKw.pop("targets")
        else:
            targets = ()

        obj.ensureExist(type, createKw=createKw)

        cls = {
            "floppy": FloppyBus,
            "ide": IdeBus,
            "sata": SataBus,
        }[type]

        sub = cls(self)
        if targets:
            if mode == "setup":
                sub.setup(obj, targets)
            elif mode == "ensure":
                sub.ensure(obj, targets)
            else:
                raise NotImplementedError(mode)

    def parentObjToMyObj(self, vm):
        return vm.storageControllers