import os

from . import (
    base,
    props,
)

class Floppy(base.Entity):
    
    def getStorageAttachKwargs(self):
        return {
            "type": "fdd",
            "medium": self.source.id,
        }


class EmptyFloppy(object):

    def __init__(self, parent):
        super(EmptyFloppy, self).__init__()
        self.parent = parent
    
    def getStorageAttachKwargs(self):
        return {
            "type": "fdd",
            "medium": "emptydrive",
        }


class Library(base.Library):
    
    entityCls = Floppy
    empty = None

    def __init__(self, *args, **kwargs):
        super(Library, self).__init__(*args, **kwargs)
        self.empty = EmptyFloppy(self)

    def fromFile(self, filename):
        if not os.path.isfile(filename):
            raise self.exceptions.MissingFile(filename)
        src = self.source.new(filename)
        return self.entityCls(src, self)