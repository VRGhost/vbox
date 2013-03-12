from .. import base

class VMBase(base.VirtualBoxEntity):
    
    vm = cli = None

    def _scheduleRefreshInfo(self):
        super(VMBase, self)._scheduleRefreshInfo()
        del self.vm.info

class VirtualMachinePart(VMBase):
    
    vm = property(lambda s: s.parent.vm)
    cli = property(lambda s: s.parent.cli)
    idx = property(lambda s: s._initId)

    def onDestroyed(self):
        """Function handler executed when VM had detected that given element is no longer present in the VM."""

    def iterIds(self):
        # This will allow for virtual part to refresh its info cache whenever
        # its parent vm executes CLI command
        return self.vm.iterIds()

class PartGroup(VirtualMachinePart):
    """An iterable part group."""

    def _getInfo(self):
        pInfo = self.parent.info
        1/0

    def __iter__(self):
        return self.info.itervalues()


    def find(self, name=None, type=None):
        if name and type:
            match = lambda cnt: (cnt.type == type) and (cnt.name == name)
        elif name:
            match = lambda cnt: cnt.name == name
        elif type:
            match = lambda cnt: cnt.type == type
        else:
            match = lambda cnt: True

        for el in self:
            if match(el):
                return el

    def get(self, *args, **kwargs):
        it = self.find(*args, **kwargs)
        return it.next()

    def create(self, name, type):
        assert not self.get(name=name)
        self.cli.manage.storagectl(
            self.vm.id, name, add=type)
        return self.get(name=name, type=type)