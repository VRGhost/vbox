import os

from .. import base

ElementGroup = base.ElementGroup
VirtualBoxEntityType = base.VirtualBoxEntityType

class VirtualBoxMedium(base.VirtualBoxEntity):

    location = property(lambda s: s.getProp("Location"))
    idProps = ("UUID", "_initId", "location")

    def getVmAttachMedium(self):
        raise NotImplementedError

    def getVmAttachType(self):
        raise NotImplementedError

class MediaType(base.VirtualBoxEntityType):
    
    emptyCls = None

    def __init__(self, *args, **kwargs):
        super(MediaType, self).__init__(*args, **kwargs)
        self.empty = self.emptyCls(self, None)

    def get(self, objId):
        if os.path.exists(objId):
            # Replace object path with normalised version
            objId = os.path.realpath(objId)
        return super(MediaType, self).get(objId)

    def getFullList(self):
        raise NotImplementedError

    def listRegisteredIds(self):
        return (el["UUID"] for el in self.getFullList())

class RemovableMedium(VirtualBoxMedium):

    fname = property(lambda s: s.location)

    def _getInfo(self):
        _id = self._initId
        if os.path.exists(_id):
            check = lambda info: os.path.realpath(info["Location"]) == _id
        else:
            check = lambda info: _id == info["UUID"]

        for el in self.parent.getFullList():
            if check(el):
                return el
        return None

    def getVmAttachMedium(self):
        return self._initId