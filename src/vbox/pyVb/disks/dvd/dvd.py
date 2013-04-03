from .. import base

class Dvd(base.RemovableMedium):

    def getVmAttachType(self):
        return "dvddrive"

class GuestAdditions(Dvd):

    fname = property(lambda s: None)

    def getVmAttachMedium(self):
        return "additions"

class EmptyDvd(GuestAdditions):

    size = property(lambda s: 0)

    def getVmAttachMedium(self):
        return "emptydrive"

    def _getInfo(self):
        return None