import functools
import threading

from . import base

class SourceProperty(object):
    """Property that is a proxy to the source object."""

    getTarget = fget = fset = fdel = None

    def __init__(self, fget, fset=None, fdel=None, getDepends=None):
        super(SourceProperty, self).__init__()
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
        super(TypeMapper, self)._doSet(obj, self.typeTo(value))

class SourceStr(TypeMapper):
    
    typeFrom = str
    typeTo = str

class SourceInt(TypeMapper):

    typeFrom = int

class OnOff(TypeMapper):

    def typeFrom(self, value):
        value = value.lower()
        assert value in ("on", "off")
        return value == "on"

    def typeTo(self, value):
        return "on" if value else "off"

class HumanReadableFileSize(TypeMapper):

    def typeFrom(self, value):
        (number, units) = value.lower().split()
        base = int(number)
        if units in ("byte", "bytes"):
            mul = 1
        elif units in ("kbyte", "kbytes"):
            mul = 1024
        elif units in ("mbyte", "mbytes"):
            mul = 1024 ** 2
        elif units in ("gbyte", "gbytes"):
            mul = 1024 ** 3
        else:
            raise NotImplementedError(units)

        return base * mul

    def typeTo(self, value):
        raise NotImplementedError(value)