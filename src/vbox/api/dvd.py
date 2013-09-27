import os

from . import (
    base,
    props,
)

class Dummy(object):

    maxSize = property(lambda s: 0)

    def __init__(self, parent):
        super(Dummy, self).__init__()
        self.parent = parent

class DVD(base.Entity):

    maxSize = property(lambda s: s.size)

    def getStorageAttachKwargs(self):
        return {
            "type": "dvddrive",
            "medium": self.source.id,
        }

    _size = None
    @property
    def size(self):
        if self._size is None:
            self._size = os.stat(self.source.id).st_size / (1024 ** 2) # size in MB
        return self._size

class EmptyDVD(Dummy):
    
    def getStorageAttachKwargs(self):
        return {
            "type": "dvddrive",
            "medium": "emptydrive",
        }

class GuestAdditionsDVD(Dummy):
    
    def getStorageAttachKwargs(self):
        return {
            "type": "dvddrive",
            "medium": "additions",
        }

class Library(base.Library):
    
    entityCls = DVD
    empty = guestAdditions = None

    def __init__(self, *args, **kwargs):
        super(Library, self).__init__(*args, **kwargs)
        self.empty = EmptyDVD(self)
        self.guestAdditions = GuestAdditionsDVD(self)

    def fromFile(self, filename):
        if not os.path.isfile(filename):
            raise self.exceptions.MissingFile(filename)
        src = self.source.new(filename)
        return self.entityCls(src, self)
