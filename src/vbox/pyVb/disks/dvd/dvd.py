from .. import base

class Dvd(base.RemovableMedium):

    def getVmAttachType(self):
        return "dvddrive"

class GuestAdditions(Dvd):

    fname = property(lambda s: None)

    def getVmAttachMedium(self):
        return "additions"

class EmptyDvd(GuestAdditions):

    def getVmAttachMedium(self):
        return "emptydrive"