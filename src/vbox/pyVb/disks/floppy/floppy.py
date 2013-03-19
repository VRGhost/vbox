from .. import base

class Floppy(base.RemovableMedium):

    def getVmAttachType(self):
        return "fdd"

class EmptyFloppy(Floppy):
    
    def getVmAttachMedium(self):
        return "emptydrive"