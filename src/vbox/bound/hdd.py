import os
import glob

from . import (
    base,
    exceptions,
)

refreshing = base.refreshing
refreshingLib = base.refreshingLib

class HDD(base.Entity):

    exceptions = exceptions

    info = base.refreshedProperty(lambda s: s.cli.manage.showHdInfo(s.id))

    def __init__(self, *args, **kwargs):
        super(HDD, self).__init__(*args, **kwargs)
        self._refreshId()

    @refreshingLib
    def unregister(self, delete=True):
        self.cli.manage.closeMedium(target=self.id, type="disk", delete=delete)
        self.library.pop(self)
    
    @refreshingLib
    def create(self, size, format="VDI", **kwargs):
        cli = self.cli
        if os.path.exists(self.id):
            raise self.exceptions.FileAlreadyExists(self.id)

        try:
            cli.manage.createHD(filename=self.id, size=size, format="vdi", **kwargs)
        except cli.exceptions.CalledProcessError as err:
            if "VERR_ALREADY_EXISTS" in str(err):
                raise self.exceptions.FileAlreadyExists(self.id)
            else:
                raise
        else:
            self._refreshId()
            assert os.path.isfile(self.id)

    def _refreshId(self):
        if os.path.splitext(self.id)[1] == '':
            match = glob.glob("{}.*".format(self.id))
            if match:
                self.id = match[0]


class Library(base.Library):

    entityCls = HDD

    @base.refreshed
    def listRegistered(self):
        out = []
        for el in self.cli.manage.list.hdds():
            out.append(self.getOrCreate(el["Location"]))
        return tuple(out)