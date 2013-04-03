from .. import base

class Floppy(base.RemovableMedium):

    def getVmAttachType(self):
        return "fdd"

class EmptyFloppy(Floppy):

    size = property(lambda s: 0)
    
    def getVmAttachMedium(self):
        return "emptydrive"

    def _getInfo(self):
        return None