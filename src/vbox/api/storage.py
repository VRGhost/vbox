import itertools
import os

from . import base

class Storage(base.Child):

    kwargName = "storage"
    expectedKwargs = {
        "hdd": lambda cnt: True,
        "optical": lambda cnt: True,
        "fdd": lambda cnt: True,
    }

    def _getHddId(self, child):
        return self.hdd.index(child)

    def _getOpticalId(self, child):
        return self.optical.index(child)

    def _getFddId(self, child):
        return self.fdd.index(child)

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

    def _getController(self):
        return self.pyVm.ide

    def _findMedia(self):
        num = 0
        for el in self._getController().iterMedia():
            obj = el[1]
            if (obj is None) or (not self._findMediaFilter(obj)):
                continue
            elif num == self.idx:
                return obj
            else:
                num += 1
        return None

    def _findMediaFilter(self, obj):
        raise NotImplementedError

class HDD(Medium):

    kwargName = "hdd"
    expectedKwargs = {
        "size": 1,
        "name": (0, 1),
    }

    defaultKwargs = {
        "name": None,
    }

    idx = property(lambda s: s.parent._getHddId(s))

    def befoureSetup(self, kwargs):
        myImage = self._findMedia()
        if myImage is None:
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

    def _findMediaFilter(self, obj):
        return obj.getVmAttachType() == "hdd"

class Removable(Medium):

    expectedKwargs = {
        "target": (0, 1)
    }

    defaultKwargs = {
        "target": lambda: None,
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

    def _findMediaFilter(self, obj):
        return obj.getVmAttachType() == "dvddrive"

class FDD(Removable):
    kwargName = "fdd"
    idx = property(lambda s: s.parent._getFddId(s))

    def _paramToPyObj(self, param):
        if param:
            img = self.pyVb.floppies.get(param)
        else:
            img = self.pyVb.floppies.empty
        return img

    def _findMediaFilter(self, obj):
        return obj.getVmAttachType() == "fdd"

    def _getController(self):
        return self.pyVm.floppy