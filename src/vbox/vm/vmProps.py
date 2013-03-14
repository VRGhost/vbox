"""Vm property getters/setters/translators."""

class VmProp(object):

    _readName = _writeName = None

    def __init__(self, name, cliName=None, control=False):
        self._readName = name
        self._control = control
        if cliName:
            self._writeName = cliName
        else:
            self._writeName = name

    def fromCli(self, val):
        return val

    def toCli(self, val):
        return val

    def __get__(self, instance, owner):
        assert instance is not None

        if callable(self._readName):
            name = self._readName(instance)
        else:
            name = self._readName
        val = instance.getProp(name)
        return self.fromCli(val)

    def __set__(self, instance, val):
        if callable(self._writeName):
            name = self._writeName(instance)
        else:
            name = self._writeName
        val = self.toCli(val)

        instance.setProp(name, val)

        cnt = self._control
        if cnt:
            if callable(cnt):
                cntName = cnt(instance)
            elif isinstance(cnt, basestring):
                cntName = cnt
            else:
                cntName = name
            kw = {cntName: val}
            instance.control(quiet=True, **kw)

class String(VmProp):
    """Just a class to explicilty state type of a property."""

class Switch(VmProp):
    """on/off property."""

    def fromCli(self, val):
        assert val in ("on", "off", None, "none")
        return val == "on"

    def toCli(self, val):
        return "on" if val else "off"

class Int(VmProp):

    def fromCli(self, val):
        return int(val)

def infoed(fn):
    def __wrapper__(self, *args, **kwargs):
        # ensure that info cache is updated
        self.info
        return fn(self, *args, **kwargs)
    return property(__wrapper__)