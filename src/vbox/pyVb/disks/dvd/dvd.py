from .. import base

class Dvd(base.RemovableMedium):

    def getVmAttachType(self):
        return "dvddrive"

class GuestAdditions(Dvd):

    def getVmAttachMedium(self):
        return "additions"

class EmptyDvd(Dvd):

    def getVmAttachMedium(self):
        return "emptydrive"