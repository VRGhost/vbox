import itertools

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
            if "name" in kwargs:
                createKw.update({
                    "autoname": False,
                    "filename": kwargs["name"],
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
            myImage = self._paramToPyObj(trg)
            self._getController().attach(myImage)
        self._pyImage = myImage

    def target():
        doc = "The target property."
        def fget(self):
            print self._pyImage
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
            controller.attach(img, slot=mySlot)
            self._pyImage = img
        def fdel(self):
            del self._target
        return locals()
    target = property(**target())

    def _paramToPyObj(self, param):
        raise NotImplementedError

class DVD(Removable):
    kwargName = "optical"
    idx = property(lambda s: s.parent._getOpticalId(s))

    def _paramToPyObj(self, param):
        if param:
            img = self.pyVb.dvds.get(value)
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
            img = self.pyVb.floppies.get(value)
        else:
            img = self.pyVb.floppies.empty
        return img

    def _findMediaFilter(self, obj):
        return obj.getVmAttachType() == "fdd"

    def _getController(self):
        return self.pyVm.floppy