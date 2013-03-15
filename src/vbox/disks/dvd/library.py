from .. import base

from . import dvd

class DvdLibrary(base.MediaType):

    cls = dvd.Dvd
    emptyCls = dvd.EmptyDvd

    def getFullList(self):
        return self.vb.cli.manage.list.dvds()
