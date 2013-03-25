from . import base

class Network(base.Child):
    kwargName = "network"

    expectedKwargs = {
        "nic": lambda cnt: True,
    }

    def _getNicId(self, obj):
        return self.nic.index(obj)

class _NicType(object):
    vbName = None

class NA(_NicType):
    """N/A for "Not Available." """
    vbName = None

class Nat(_NicType):
    vbName = "nat"

class HostOnly(_NicType):
    vbName = "hostonly"


class _NicTypes(object):
    
    def __init__(self):
        typeCls = (NA, Nat, HostOnly)
        self._types = dict((cls.__name__, cls()) for cls in typeCls)

    def find(self, name):
        try:
            return self[name]
        except KeyError:
            pass
        for el in self._types.itervalues():
            if el.vbName == name:
                return el
        raise KeyError(name)

    def __getitem__(self, name):
        return self._types[name]

    def __getattr__(self, name):
        return self[name]


NicTypes = _NicTypes()

class NIC(base.Child):
    kwargName = "nic"
    types = NicTypes

    idx = property(lambda s: s.parent._getNicId(s))

    expectedKwargs = {
        "type": 1,
    }

    def befoureSetup(self, kwargs):
        # +1 as virtualbox numbers NICs starting with 1
        self._pyObject = self.pyVm.nics[self.idx + 1]

    def type():
        doc = "The type property."
        def fget(self):
            return self.types.find(self._pyObject.type)
        def fset(self, value):
            self._pyObject.type = value.vbName
        return locals()
    type = property(**type())