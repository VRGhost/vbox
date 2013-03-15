from .. import base

ElementGroup = base.ElementGroup
VirtualBoxEntityType = base.VirtualBoxEntityType

class VirtualBoxMedium(base.VirtualBoxEntity):

    def getVmAttachMedium(self):
        raise NotImplementedError

    def getVmAttachType(self):
        raise NotImplementedError

class MediaType(base.VirtualBoxEntityType):
    
    emptyCls = None

    def __init__(self, *args, **kwargs):
        super(MediaType, self).__init__(*args, **kwargs)
        self.empty = self.emptyCls(self, None)

    def getFullList(self):
        raise NotImplementedError

    def listRegisteredIds(self):
        return (el["UUID"] for el in self.getFullList())

class RemovableMedium(VirtualBoxMedium):

    def _getInfo(self):
        for el in self.parent.getFullList():
            if self._initId in (el["UUID"], el["Location"]):
                return el
        return None

    def getVmAttachMedium(self):
        return self._initId