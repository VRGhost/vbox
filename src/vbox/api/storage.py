import itertools
import os

from . import base

def _getMedia(self, typ):
    for cnt in self.pyVm.controllers:
        for (name, media) in cnt.iterMedia():
            if typ.findMediaFilter(media):
                yield (cnt.type, media)

class Storage(base.Child):

    kwargName = "storage"
    expectedKwargs = {
        "hdd": lambda cnt: True,
        "optical": lambda cnt: True,
        "fdd": lambda cnt: True,
    }
    defaultKwargs = {
        "hdd": lambda s: [HDD(controller=cnt, size=media.size)
            for (cnt, media) in _getMedia(s, HDD)],
    }

    def _getHddId(self, child):
        return self._findId(self.hdd, child)    

    def _getOpticalId(self, child):
        return self._findId(self.optical, child)

    def _getFddId(self, child):
        return self._findId(self.fdd, child)

    def _findId(self, sequence, child):
        return sequence.index(child)

    def _iterControllers(self, type):
        if type == "ide":
            return (self.pyVm.ide, )
        elif type == "sata":
            return (self.pyVm.sata, )
        elif type == "floppy":
            return (self.pyVm.floppy, )
        else:
            raise NotImplementedError(type)

    def _findMedia(self, pyObj, controller):
        idx = pyObj.idx
        num = 0
        for cnt in self._iterControllers(controller):
            for (slot, obj) in cnt.iterMedia():
                if not pyObj.findMediaFilter(obj):
                    continue
                elif num == idx:
                    return obj
                else:
                    num += 1
        return None

    @property
    def dvd(self):
        try:
            return self.dvds().next()
        except StopIteration:
            return None

    def dvds(self):
        return iter(self.optical)

class Medium(base.Child):
    idx = None
    _pyImage = None

    @classmethod
    def findMediaFilter(self, obj):
        raise NotImplementedError

class HDD(Medium):

    kwargName = "hdd"
    expectedKwargs = {
        "controller": (0, 1),
        "size": 1,
        "name": (0, 1),
    }

    defaultKwargs = {
        "name": None,
        "controller": "ide",
    }

    idx = property(lambda s: s.parent._getHddId(s))

    def befoureSetup(self, kwargs):
        myImage = self.parent._findMedia(
            self, kwargs["controller"])
        if myImage is None:
            print kwargs
            1/0
            createKw = {
                "size": kwargs["size"],
            }

            fname = kwargs.get("name")
            rootDir = self.vm.general.directory
            if rootDir and fname:
                fname = os.path.join(rootDir, fname)
                autoName = False
            elif rootDir and (not fname):
                fname = os.path.join(rootDir, "unnamed_disk")
                autoName = True
            elif fname and (not rootDir):
                # fname = fname
                autoName = False
            else:
                assert fname is None
                assert rootDir is None
                autoName = True

            createKw.update({
                "autoname": autoName,
                "filename": fname
            })

            myImage = self.pyVb.hdds.create(**createKw)
            self._getController().attach(myImage)

        assert myImage is not None
        self._pyImage = myImage

    def size():
        doc = "The size property."
        def fget(self):
            if self._pyImage:
                return self._pyImage.size
            else:
                return None
        def fset(self, value):
            if self._pyImage and (self.size != value):
                self._pyImage.size = value
        return locals()
    size = property(**size())

    @classmethod
    def findMediaFilter(cls, obj):
        return obj.getVmAttachType() == "hdd"

class Removable(Medium):

    expectedKwargs = {
        "target": (0, 1)
    }

    defaultKwargs = {
        "target": lambda s: None,
    }

    def befoureSetup(self, kwargs):
        myImage = self._findMedia()
        if myImage is None:
            trg = kwargs["target"]
            slot = self._getController().attach(self._paramToPyObj(trg))
            myImage = self._getController().getMedia(slot)
        self._pyImage = myImage

    def target():
        doc = "The target property."
        def fget(self):
            if self._pyImage:
                rv = self._pyImage.fname
            else:
                rv = None
            return rv
        def fset(self, value):
            img = self._paramToPyObj(value)
            oldImg = self._pyImage
            if img == oldImg:
                return
            assert oldImg
            controller = self._getController()
            mySlot = controller.findSlotOf(oldImg)
            assert mySlot, mySlot
            controller.attach(img, slot=mySlot)
            self._pyImage = img
        return locals()
    target = property(**target())

    def _paramToPyObj(self, param):
        raise NotImplementedError

class DVD(Removable):
    kwargName = "optical"
    idx = property(lambda s: s.parent._getOpticalId(s))

    def _paramToPyObj(self, param):
        if param:
            img = self.pyVb.dvds.get(param)
        else:
            img = self.pyVb.dvds.empty
        return img

    @classmethod
    def findMediaFilter(cls, obj):
        return obj.getVmAttachType() == "dvddrive"

class FDD(Removable):
    kwargName = "fdd"
    idx = property(lambda s: s.parent._getFddId(s))

    defaultKwargs = Removable.defaultKwargs.copy()
    defaultKwargs["controller"] = "floppy"

    def _paramToPyObj(self, param):
        if param:
            img = self.pyVb.floppies.get(param)
        else:
            img = self.pyVb.floppies.empty
        return img


    @classmethod
    def findMediaFilter(cls, obj):
        return obj.getVmAttachType() == "fdd"