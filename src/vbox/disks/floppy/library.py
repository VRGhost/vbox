from .. import base

from . import floppy

class FloppyLibrary(base.MediaType):

    cls = floppy.Floppy
    emptyCls = floppy.EmptyFloppy

    def getFullList(self):
        return self.vb.cli.manage.list.floppies()