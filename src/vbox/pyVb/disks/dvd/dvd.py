from .. import base

class Dvd(base.RemovableMedium):

    fname = property(lambda s: s.info["Location"])

    def getVmAttachType(self):
        return "dvddrive"

class GuestAdditions(Dvd):

    fname = property(lambda s: None)

    def getVmAttachMedium(self):
        return "additions"

class EmptyDvd(GuestAdditions):

    def getVmAttachMedium(self):
        return "emptydrive"