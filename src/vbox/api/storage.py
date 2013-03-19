import itertools

from . import base

class Storage(base.Child):

    kwargName = "storage"
    expectedKwargs = {
        "hdd": lambda cnt: True,
        "optical": lambda cnt: True,
    }

    def _getHddId(self, child):
        return self.hdd.index(child)

    def _getOpticalId(self, child):
        return self.optical.index(child)

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

    def _findMedia(self, filter):
        num = 0
        for el in self._getController().iterMedia():
            obj = el[1]
            if (obj is None) or (not filter(obj)):
                continue
            elif num == self.idx:
                return obj
            else:
                num += 1
        return None

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
        myImage = self._findMedia(lambda el: el.getVmAttachType() == "hdd")

        if myImage is None:
            createKw = {
                "size": kwargs["size"],
            }
            if "name" in kwargs:
                createKw.update({
                    "autoname": False,
                    "filename": kwargs["name"]
                })
            myImage = self.pyVb.hdds.create(createKw)
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

class DVD(Medium):

    kwargName = "optical"
    expectedKwargs = {
        "target": (0, 1)
    }

    defaultKwargs = {
        "target": lambda: None,
    }
    idx = property(lambda s: s.parent._getOpticalId(s))

    def befoureSetup(self, kwargs):
        myImage = self._findMedia(lambda el: el.getVmAttachType() == "dvddrive")
        if myImage is None:
            trg = kwargs["target"]
            if trg:
                myImage = self.pyVb.dvds.get(trg)
            else:
                myImage = self.pyVb.dvds.empty
            self._getController().attach(myImage)
        self._pyImage = myImage

    def target():
        doc = "The target property."
        def fget(self):
            return self._pyImage.fname
        def fset(self, value):
            if not value:
                img = self.pyVb.dvds.empty
            else:
                img = self.pyVb.dvds.get(value)
            self._target = value
            raise NotImplementedError
        def fdel(self):
            del self._target
        return locals()
    target = property(**target())