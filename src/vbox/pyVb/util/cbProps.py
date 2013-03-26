"""Vm property getters/setters/translators."""

class Prop(object):

    _readName = _writeName = None

    def __init__(self, name, cliName=None, extraCb=False):
        self._readName = name
        self.extraCb = extraCb
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

        extraCb = self.extraCb
        if extraCb:
            extraCb(instance, val)

class String(Prop):
    """Just a class to explicilty state type of a property."""

class Switch(Prop):
    """on/off property."""

    trueVals = ("on", )
    falseVals = ("off", "none")
    outTrue = "on"
    outFalse = "off"

    def fromCli(self, val):
        assert (val in self.trueVals) or \
            (val in self.falseVals) or \
            (val is None), val
        return val in self.trueVals

    def toCli(self, val):
        return self.outTrue if val else self.outFalse

class Int(Prop):

    def fromCli(self, val):
        return int(val)

    def toCli(self, val):
        return int(val)

class Tuple(Prop):

    def __init__(self, name, sep, *args, **kwargs):
        super(Tuple, self).__init__(name, *args, **kwargs)
        self.sep = sep

    def fromCli(self, val):
        out = (el.strip() for el in val.split(self.sep))
        return tuple(el for el in out if el)

    def toCli(self, val):
        return self.sep.join(str(el) for el in val)