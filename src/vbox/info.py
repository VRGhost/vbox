"""Global system info object.

Data that is managed by it should not change within single API-enabled program run.

"""

from . import base

class _OsType(object):

    def __init__(self, data):
        super(_OsType, self).__init__()
        self._data = out = {}

        mappers = {
            "64 bit": lambda val: (val.lower() == "true")
        }
        for (name, value) in data.iteritems():
            if name in mappers:
                value = mappers[name](value)
            out[name.lower().replace(' ', '')] = value

    def __getitem__(self, name):
        for el in self._iterPossibleNames(name):
            try:
                return self._data[el]
            except KeyError:
                continue
        else:
            # Not found
            raise KeyError(name)

    def _iterPossibleNames(self, name):
        name = name.lower().replace(' ', '')
        yield name

    def __getattr__(self, name):
        return self[name]

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self._data)

class _Ostypes(base.VirtualBoxElement):
    
    def __init__(self, *args, **kwargs):
        super(_Ostypes, self).__init__(*args, **kwargs)
        self._data = [_OsType(el)
            for el in self.vb.cli.manage.list.ostypes()]

    def find(self, name):
        for el in self:
            flds = (el.description, el.id)
            if name in flds:
                return el
        return None

    def __iter__(self):
        return iter(self._data)

class _SystemProperties(base.VirtualBoxElement):
    pass

class _HostInfo(base.VirtualBoxElement):
    pass

class Info(base.VirtualBoxElement):

    def __init__(self, *args, **kwargs):
        super(Info, self).__init__(*args, **kwargs)
        self.ostypes = _Ostypes(self)
        self.system = _SystemProperties(self)
        self.host = _HostInfo(self)