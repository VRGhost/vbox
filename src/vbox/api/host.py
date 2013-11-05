import os
from . import base, props

class FuzzyPath(props.Str):

    def typeFrom(self, val):
        return val.replace('/', os.sep).replace('\\', os.sep)

class OsType(object):

    def __init__(self, srcDict):
        super(OsType, self).__init__()

        self._data = {}
        _remaining = srcDict.copy()

        for (src, dst) in [
            ("Family Desc", "family_desc"),
            ("Description", "description"),
            ("64 bit", "64_bit"),
            ("Family ID", "family_id"),
            ("ID", "id"),
        ]:
            self._data[dst] = _remaining.pop(src)

        self._data["64_bit"] = (self._data["64_bit"].lower() == "true")

        if _remaining:
            raise Exception("Unprocessed fields remain: {}".format(_remaining.keys()))

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self._data)

class Host(base.Library):

    defaultVmDir = FuzzyPath(lambda s: s.source.properties["Default machine folder"])
    knownOsTypes = props.SourceProperty(lambda s: tuple(OsType(el) for el in s.source.knownOsTypes))