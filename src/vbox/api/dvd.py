from . import (
    base,
    props,
)

class Dummy(object):

    def __init__(self, parent):
        super(Dummy, self).__init__()
        self.parent = parent

class DVD(base.Entity):
    pass

class EmptyDVD(Dummy):
    
    def getStorageAttachKwargs(self):
        return {
            "type": "dvddrive",
            "medium": "emptydrive",
        }

class GuestAdditionsDVD(Dummy):
    pass

class Library(base.Library):
    
    empty = guestAdditions = None

    def __init__(self, *args, **kwargs):
        super(Library, self).__init__(*args, **kwargs)
        self.empty = EmptyDVD(self)
        self.guestAdditions = GuestAdditionsDVD(self)
