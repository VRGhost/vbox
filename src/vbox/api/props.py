import functools
import threading

from . import base

class SourceProperty(object):
    """Property that is a proxy to the source object."""

    getTarget = fget = fset = fdel = None

    def __init__(self, fget, fset=None, fdel=None, getDepends=None, doc=None):
        super(SourceProperty, self).__init__()
        if doc:
            self.__doc__ = doc
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if getDepends:
            assert callable(getDepends)
            self.getDepends = getDepends
        else:
            self.getDepends = lambda obj: (obj, )

        self.accessLock = threading.Lock()

    def __get__(self, obj, type=None):
        name = self.getTargetPropName(obj)
        try:
            rv = getattr(obj, name)
        except AttributeError:
            with self.accessLock:
                try:
                    # Field might have been created since.
                    rv = getattr(obj, name)
                except AttributeError:
                    rv = self.buildGetter(obj)
                    setattr(obj, name, rv)

        return rv()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("Can't set attribute")
        self._doSet(obj, value)

    def _doSet(self, obj, value):
        if value == self.__get__(obj):
            return
        self.fset(obj, value)
        self.clearCache(obj)

    def __delete__(self, obj):
        if not self.fset:
            raise AttributeError("Can't delete attribute")
        self.fdel(obj)
        self.clearCache(obj)

    def setter(self, func):
        if self.fset is None:
            self.fset = func
        else:
            raise AttributeError("Setter already defined.")
        return self

    def clearCache(self, obj):
        with self.accessLock:
            name = self.getTargetPropName(obj)
            try:
                handle = getattr(obj, name)
            except AttributeError:
                pass
            else:
                handle.clearCache(self)

    def getTargetPropName(self, obj):
        return "_{!r}({!r})_getter_for_{!r}({!r})".format(
            self, id(self), obj, id(obj)
        )

    def buildGetter(self, obj):
        boundFget = lambda: self.fget(obj)
        return base.ProxyRefreshTrail(
            func=functools.wraps(self.fget)(boundFget),
            depends=self.getDepends(obj),
        )

class TypeMapper(SourceProperty):

    typeFrom = str
    typeTo = str
    nonable = False

    def __init__(self, fget, fset=None, fdel=None, getDepends=None, nonable=True):
        super(TypeMapper, self).__init__(fget, fset, fdel, getDepends)
        self.nonable = nonable

    def buildGetter(self, obj):

        @functools.wraps(self.fget)
        def _wrapper(*args, **kwargs):
            untyped = self.fget(obj, *args, **kwargs)
            try:
                rv = self.typeFrom(untyped)
            except TypeError:
                if (untyped is None) and self.nonable:
                    rv = untyped
                else:
                    raise
            return rv

        return base.ProxyRefreshTrail(
            func=_wrapper,
            depends=self.getDepends(obj),
        )

    def _doSet(self, obj, value):
        if value == self.__get__(obj):
            return
        super(TypeMapper, self)._doSet(obj, self.typeTo(value))

class Str(TypeMapper):

    typeFrom = str
    typeTo = str

class StrOrNone(TypeMapper):

    def typeFrom(self, val):
        if val == "none":
            rv = None
        else:
            rv = val
        return rv

    def typeTo(self, val):
        if val:
            rv = val
        else:
            rv = "none"
        return rv

class Int(TypeMapper):

    typeFrom = int

class OnOff(TypeMapper):

    def typeFrom(self, value):
        if value is None:
            return None

        value = value.lower()
        assert value in ("on", "off")
        return value == "on"

    def typeTo(self, value):
        return "on" if value else "off"

class HumanReadableFileSize(TypeMapper):

    def __init__(self, resultUnits="byte", float=False, **kwargs):
        super(HumanReadableFileSize, self).__init__(**kwargs)
        self._rvUnits = resultUnits
        self._float = float

    def typeFrom(self, value):
        (number, units) = value.lower().split()
        base = int(number)
        baseMul = self.getMul(units)
        rvMul = self.getMul(self._rvUnits)

        byteRv = base * baseMul
        if self._float:
            byteRv = float(byteRv)
        if rvMul > 1:
            rv = byteRv / rvMul
        else:
            rv = byteRv

        return rv

    def getMul(self, name):
        name = name.lower()
        if name.endswith("es"):
            name = name[:-1] # -bytes --> -byte
        assert name.endswith("byte"), name

        if name == "byte":
            mul = 1
        elif name == "kbyte":
            mul = 1024
        elif name == "mbyte":
            mul = 1024 ** 2
        elif name == "gbyte":
            mul = 1024 ** 3
        else:
            raise NotImplementedError(name)
        return mul

    def typeTo(self, value):
        raise NotImplementedError(value)

def modify(name):
    """vboxmanage modify callback property."""
    return {
        "fget": lambda self: self.source.info.get(name),
        "fset": lambda self, value: self.source.modify(**{name: value}),
    }

def modifySelfRef(name):
    def _fget(self):
        propName = name.format(self=self)
        return self.source.info.get(propName)
    def _fset(self, value):
        propName = name.format(self=self)
        self.source.modify(**{propName: value})
    return {"fget": _fget, "fset": _fset}