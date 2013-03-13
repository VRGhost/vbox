import os
import threading

from . import (
    base,
    cli, 
    hdd,
    info,
    vm,
)

class _HDD(base.VirtualBoxEntityType):
    """HDD interface."""

    cls = hdd.HDD

    def create(self, size, filename=None, autoname=True, format="VDI", variant="Standard"):
        super(_HDD, self).create()
        if autoname:
            lst = tuple(self.list())
            idx = 0
            prefix = filename or "auto_created_hdd"
            genName = lambda : "{}_{}.{}".format(prefix, idx, format.lower())
            while (genName() in lst) or os.path.exists(genName()):
                idx += 1
            assert genName() not in lst
            filename = genName()

        createhd = lambda: self.vb.cli.manage.createhd(
            filename=filename, size=size, format=format, variant=variant)
        hddExistsMsg = "cannot register the hard disk"
        hddExistsError = False

        try:
            createhd()
        except cli.CmdError as err:
            if autoname and (hddExistsMsg in err.output.lower()):
                hddExistsError = True
            else:
                raise

        if hddExistsError:
            assert autoname
            assert genName

            while hddExistsError:
                # remove old file, if it was created
                if os.path.exists(filename):
                    os.unlink(filename)
                idx += 1
                filename = genName()
                try:
                    createhd()
                except cli.CmdError as err:
                    if hddExistsMsg in err.output.lower():
                        continue
                    raise
                else:
                    # creation succeeded
                    break

        return self.get(filename)

    def listRegisteredIds(self):
        return [el["UUID"] for el in self.vb.cli.manage.list.hdds()]

class _VMs(base.VirtualBoxEntityType):
    
    cls = vm.VM

    def create(self, autoname=True, ostype=None, **kwargs):
        super(_VMs, self).create()
        name = kwargs.pop("name", "unnamed_machine")
        existing = [vm.name for vm in self.list()]
        if name in existing:
            if not autoname:
                raise Exception("Virtual machine {!r} already exists.".format(name))
            idx = 1
            genName = lambda: "{} ({})".format(name, idx)
            while genName() in existing:
                idx += 1
            name = genName()

        kwargs["name"] = name

        if ostype:
            # Verify os type
            found = self.vb.info.ostypes.find(ostype)
            if not found:
                raise Exception("OS type {!r} not found".format(ostype))
            kwargs["ostype"] = found.id            

        out = self.vb.cli.manage.createvm(**kwargs)
        out = cli.util.parseParams(out)
        return self.get(out["Settings file"])

    def listRegisteredIds(self):
        return self.vb.cli.manage.list.vms().values()

class VirtualBox(base.ElementGroup):
    """Python version of virtualbox program/service."""

    
    # Each object in this program should have pointer to the virtualbox object
    vb = property(lambda self: self)
    parent = None

    def __init__(self):
        self.cli = cli.CommandLineInterface(self)
        self.info = info.Info(self)
        super(VirtualBox, self).__init__()

    def getElements(self):
        return {
            "hdd": _HDD(self),
            "vms": _VMs(self),
            "mediums": vm.mediums.HostMediums(self)
        }
