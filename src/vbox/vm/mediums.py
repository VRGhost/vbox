from .. import base

class RemovableMedium(base.VirtualBoxMedium):

    def _getInfo(self):
        for el in self.parent.getFullList():
            if self._initId in (el["UUID"], el["Location"]):
                return el
        return None

    def getVmAttachMedium(self):
        return self._initId

class Floppy(RemovableMedium):

    def getVmAttachType(self):
        return "fdd"

class Dvd(RemovableMedium):

    def getVmAttachType(self):
        return "dvddrive"

class GuestAdditions(Dvd):

    def getVmAttachMedium(self):
        return "additions"

class EmptyDvd(Dvd):

    def getVmAttachMedium(self):
        return "emptydrive"

class EmptyFloppy(Floppy):
    
    def getVmAttachMedium(self):
        return "emptydrive"

class MediaType(base.VirtualBoxEntityType):
    
    emptyCls = None

    def __init__(self, *args, **kwargs):
        super(MediaType, self).__init__(*args, **kwargs)
        self.empty = self.emptyCls(self, None)

    def getFullList(self):
        raise NotImplementedError

    def listRegisteredIds(self):
        return (el["UUID"] for el in self.getFullList())

class DvdType(MediaType):

    cls = Dvd
    emptyCls = EmptyDvd

    def getFullList(self):
        return self.vb.cli.manage.list.dvds()

class FloppyType(MediaType):

    cls = Floppy
    emptyCls = EmptyFloppy

    def getFullList(self):
        return self.vb.cli.manage.list.floppies()
        
class HostMediums(base.ElementGroup):
    
    def __init__(self, vb):
        self.vb = vb
        super(HostMediums, self).__init__()        

    def getElements(self):
        return {
            "dvd":  DvdType(self.vb),
            "floppy": FloppyType(self.vb)
        }