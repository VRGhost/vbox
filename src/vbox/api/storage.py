import collections
import itertools
import os
import threading

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
        "optical": lambda s: [DVD(controller=cnt)
            for (cnt, media) in _getMedia(s, DVD)],
        "fdd": lambda s: [FDD(controller=cnt)
            for (cnt, media) in _getMedia(s, FDD)],
    }


    _mediaFinderCache = None
    def _findMedia(self, medium, controller):
        if self._mediaFinderCache is None:
            self._mediaFinderCache = {}
        if controller not in self._mediaFinderCache:
            self._mediaFinderCache[controller] = self._iterAllMedia(controller)
        gen = self._mediaFinderCache[controller]
        if gen is not None:
            try:
                return gen.next()
            except StopIteration:
                self._mediaFinderCache[controller] = None
        return None

    def _iterAllMedia(self, controllerType):
        for cnt in self._iterControllers(controllerType):
            for (slot, obj) in cnt.iterMedia():
                yield cnt, slot, obj

    def _iterControllers(self, type):
        # Ensure that at least one controller of a given type
        # exists
        if type == "ide":
            self.pyVm.ide
        elif type == "sata":
            self.pyVm.sata
        elif type == "floppy":
            self.pyVm.floppy
        else:
            raise NotImplementedError(type)
        return self.pyVm.controllers.find(type=type)

    def _findEmptyController(self, type):
        """Find controller that has at least one empty slot to attach new device to."""
        return self._iterControllers(type).next()

    def _iterAttachedImages(self):
        for medium in self._iterMediums():
            if medium.initialised and medium._pyImage:
                yield medium._pyImage

    def _iterMediums(self):
        assert self.initialised
        return itertools.chain(self.hdd, self.optical, self.fdd)

    @property
    def dvd(self):
        try:
            return self.dvds().next()
        except StopIteration:
            return None

    def dvds(self):
        return iter(self.optical)

class Medium(base.Child):
    _pyImage = None

    expectedKwargs = {
        "controller": (0, 1),
    }
    defaultKwargs = {
        "controller": lambda s: "ide",
    }

    @classmethod
    def findMediaFilter(self, obj):
        raise NotImplementedError

class HDD(Medium):

    kwargName = "hdd"
    expectedKwargs = Medium.expectedKwargs.copy()
    expectedKwargs.update({
        "size": 1,
        "name": (0, 1),
    })

    defaultKwargs = Medium.defaultKwargs.copy()
    defaultKwargs.update({
        "name": None,
    })

    def befoureSetup(self, kwargs):
        media = self.parent._findMedia(
            self, kwargs["controller"])
        if media is None:
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
            controller = self.parent._findEmptyController(kwargs["controller"])
            slot = controller.attach(myImage)
        else:
            (controller, slot, myImage ) = media
        assert myImage is not None
        self._pyImage = myImage
        self._pyController = controller
        self._pySlot = slot

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

    expectedKwargs = Medium.expectedKwargs.copy()
    expectedKwargs.update({
        "target": (0, 1)
    })

    defaultKwargs = Medium.defaultKwargs.copy()
    defaultKwargs.update({
        "target": lambda s: None,
    })

    def befoureSetup(self, kwargs):
        media = self.parent._findMedia(
            self, kwargs["controller"])
        if media is None:
            trg = kwargs["target"]
            controller = self.parent._findEmptyController(kwargs["controller"])
            slot = controller.attach(self._paramToPyObj(trg))
            myImage = controller.getMedia(slot)
        else:
            (controller, slot, myImage ) = media

        self._pyImage = myImage
        self._pyController = controller
        self._pySlot = slot

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
            self._pyController.attach(img, slot=self._pySlot)
            self._pyImage = img
        return locals()
    target = property(**target())

    def _paramToPyObj(self, param):
        raise NotImplementedError

class DVD(Removable):
    kwargName = "optical"

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