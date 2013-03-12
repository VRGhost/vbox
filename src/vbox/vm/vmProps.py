"""Vm property getters/setters/translators."""

class VmProp(object):

    _readName = _writeName = None

    def __init__(self, name, cliName=None):
        self._readName = name
        if cliName:
            self._writeName = cliName
        else:
            self._writeName = name

    def fromCli(self, val):
        return val

    def toCli(self, val):
        return val

    def __get__(self, instance, owner):
        val = instance.getProp(self._readName)
        return self.fromCli(val)

    def __set__(self, instance, val):
        val = self.toCli(val)
        return instance.setProp(self._writeName, val)

class Switch(VmProp):
    """on/off property."""

    def fromCli(self, val):
        assert val in ("on", "off")
        return val == "on"

    def toCli(self, val):
        return bool(val)

class Int(VmProp):

    def fromCli(self, val):
        return int(val)

def infoed(fn):
    def __wrapper__(self, *args, **kwargs):
        # ensure that info cache is updated
        self.info
        return fn(self, *args, **kwargs)
    return property(__wrapper__)