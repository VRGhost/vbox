from .. import base

VirtualBoxEntity = base.VirtualBoxEntity
VirtualBoxEntityType = base.VirtualBoxEntityType

class VmElement(base.InfoKeeper):
    vm = property(lambda s: s.parent.vm)
    cli = property(lambda s: s.parent.cli)

    _vmInfo = None
    @property
    def info(self):
        if self.vm.info != self._vmInfo:
            self.updateInfo(force=True)
            self._vmInfo = self.vm.info.copy()
        return super(VmElement, self).info

class VirtualMachinePart(VmElement):
    
    _initId = None
    idx = property(lambda s: s._initId)

    def __init__(self, parent, id):
        super(VirtualMachinePart, self).__init__(parent)
        self._initId = id

    def onDestroyed(self):
        """Function handler executed when VM had detected that given element is no longer present in the VM."""

    def getPropName(self, name):
        """Function to perform tranlslation from name local to the element to the name global for the whole VM."""
        return name

    def getProp(self, name):
        name = self.getPropName(name)
        return super(VirtualMachinePart, self).getProp(name)

    def setProp(self, name, value):
        name = self.getPropName(name)
        return self.vm.setProp(name, value)

    def control(self, params, quiet=False):
        print params
        newParams = dict((self.getPropName(name), value)
            for (name, value) in params.iteritems())
        return self.vm.control(newParams, quiet=quiet)

class PartGroup(VmElement):
    """An iterable part group."""

    childCls = parentRe = None

    def iterkeys(self):
        if self.info:
            rv = iter(self.info)
        else:
            rv = iter(())
        return rv

    def find(self, name=None, type=None):
        if name and type:
            match = lambda cnt: (cnt.type == type) and (cnt.name == name)
        elif name:
            match = lambda cnt: cnt.name == name
        elif type:
            match = lambda cnt: cnt.type == type
        else:
            match = lambda cnt: True

        if self.info:
            for el in self.info.itervalues():
                if match(el):
                    yield el

    def get(self, *args, **kwargs):
        it = self.find(*args, **kwargs)
        try:
            return it.next()
        except StopIteration:
            return None

    def create(self, name, type):
        assert not self.get(name=name)
        self.cli.manage.storagectl(
            self.vm.id, name, add=type)
        rv = self.get(name=name, type=type)
        assert rv
        return rv

    def __iter__(self):
        if self.info:
            rv = self.info.itervalues()
        else:
            rv = iter(())
        return rv

    def __len__(self):
        return len(self.info)

    def __getitem__(self, key):
        return self.info[key]

    def _getInfo(self):
        pInfo = self.parent.info

        if not pInfo:
            return None

        parentRe = self.parentRe

        out = {}

        controllerIds = set()
        for name in pInfo.iterkeys():
            match = parentRe.match(name)
            if match:
                elId = match.group(1)
                elId = int(elId)
                controllerIds.add(elId)

        if self._info:
            existing = frozenset(self._info.keys())
        else:
            existing = frozenset()

        for destroyed in (existing - controllerIds):
            obj = self._info[destroyed]
            obj.onDestroyed()

        for preserved in (existing.intersection(controllerIds)):
            out[preserved] = self._info[preserved]

        cls = self.childCls
        for added in (controllerIds - existing):
            out[added] = cls(self, added)
        
        return out