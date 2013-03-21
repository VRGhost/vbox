import os
import glob

from vbox import cli
from .. import base
from . import hdd

class HddLibrary(base.VirtualBoxEntityType):
    """HDD interface."""

    cls = hdd.HDD

    def clone(self, source, filename=None, autoname=True,
        **kwargs
    ):
        if not filename:
            filename = "{} Clone".format(source)
        nameGen = self._nameGen(filename, autoname)
        clonehd = lambda fname: self.vb.cli.manage.clonehd(
            source, fname, **kwargs)

        for name in nameGen:
            clonehd(name)
            break

        assert os.path.exists(name)
        return self.get(name)

    def create(self, 
        size, filename=None, autoname=True,
        format="VDI", variant="Standard"
    ):
        super(HddLibrary, self).create()

        nameGen = self._nameGen(filename, autoname)

        createhd = lambda fname: self.vb.cli.manage.createhd(
            filename=fname, size=int(size), format=format, variant=variant)
        hddExistsMsgs = (
            "cannot register the hard disk",
            "(VERR_ALREADY_EXISTS)".lower(),
        )
        nonCriticalError = lambda err: any(msg in err.output.lower() for msg in hddExistsMsgs)
        hddExistsError = False

        for basename in nameGen:
            hddName = "{}.{}".format(basename, format.lower())
            try:
                createhd(hddName)
            except cli.CmdError as err:
                if autoname and nonCriticalError(err):
                    hddExistsError = True
                else:
                    raise
            else:
                break
        else:
            raise Exception("Failed to create HDD.")

        return self.get(hddName)

    def _nameGen(self, baseName, autoname):
        baseName = baseName or "auto_created_hdd"
        lst = tuple(el.name for el in self.list())
        isExisting = lambda name: (name in lst) or glob.glob("{}.*".format(name))

        if not isExisting(baseName):
            yield baseName

        if autoname:
            idx = 0
            while True:
                idx += 1
                name = "{}_{}".format(baseName, idx)
                if not isExisting(name):
                    yield name

    def listRegisteredIds(self):
        return [el["UUID"] for el in self.vb.cli.manage.list.hdds()]