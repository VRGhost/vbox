import os

from . import (
    base,
    cli, 
    hdd,
    vm,
    )

class _HDD(base.VirtualBoxEntityType):
    """HDD interface."""

    cls = hdd.HDD

    def create(self, size, filename=None, format="VDI", variant="Standard"):
        super(_HDD, self).create()
        if not filename:
            lst = self.list()
            idx = 0
            genName = lambda : "auto_created_hdd_{}.{}".format(idx, format.lower())
            while (genName() in lst) or os.path.exists(genName()):
                idx += 1
            assert genName() not in lst
            filename = genName()
        self.vb.cli.manage.createhd(filename=filename, size=size, format=format, variant=variant)
        return self.get(filename)

    def listRegisteredIds(self):
        return []

class _VMs(base.VirtualBoxEntityType):
    
    cls = vm.VM

    def create(self, autoname=True, **kwargs):
        super(_VMs, self).create()
        name = kwargs.pop("name", "unnamed_machine")
        existing = [vm.name for vm in self.list()]
        if name in existing:
            if not autoname:
                raise Exception("Virtual machine {!r} already exists.".format(name))
            idx = 0
            genName = lambda: "{} ({})".format(name, idx)
            while genName() in existing:
                idx += 1
            name = genName()

        kwargs["name"] = name
        out = self.vb.cli.manage.createvm(**kwargs)
        return self.get(out["Settings file"])

    def listRegisteredIds(self):
        return self.vb.cli.manage.list.vms().values()

class _VbInfo(base.VirtualBoxEntityType):
    
    @property
    def system(self):
        return self.vb.cli.manage.list.systemproperties()

    @property
    def host(self):
        return self.vb.cli.manage.list.hostinfo()

class VirtualBox(object):
    """Python version of virtualbox program/service."""

    list = property(lambda s: s.cli.manage.list)

    class cli(object):
        manage = None

    def __init__(self):
        self.cli.manage = cli.VBoxManage()
        self.info = _VbInfo(self)
        self._elements = {
            "hdd": _HDD(self),
            "vms": _VMs(self),
        }
        for (name, obj) in self._elements.iteritems():
            setattr(self, name, obj)

    def getInvalidObjects(self):
        for typ in self._elements.itervalues():
            for el in typ.getInvalidObjects():
                yield el

    def find(self, uuid):
        for typ in self._elements.itervalues():
            obj = typ.find(uuid)
            if obj is not None:
                return obj
