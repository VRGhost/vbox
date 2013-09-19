import functools
import threading

from . import base

class SourceProperty(object):
    """Property that is a proxy to the source object."""

    def __init__(self, fget, fset=None, fdel=None):
        super(SourceProperty, self).__init__()
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.accessLock = threading.Lock()

    def __get__(self, obj, type=None):
        name = "_{!r}_getter_for_{!r}".format(self, obj)
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
        self.fset(obj, value)
        self.refresh(obj)

    def __delete__(self, obj):
        if not self.fset:
            raise AttributeError("Can't delete attribute")
        self.fdel(obj)
        self.refresh(obj)

    def refresh(self, obj):
        with self.accessLock:
            name = "_{!r}_getter_for_{!r}".format(self, obj)
            try:
                handle = getattr(obj, name)
            except AttributeError:
                pass
            else:
                handle.refresh()

    def buildGetter(self, obj):
        return base.SourceTrail(obj, self.fget)

class TypeMapper(SourceProperty):

    typeFrom = str
    typeTo = str
    nonable = False

    def __init__(self, fget, fset=None, fdel=None, nonable=True):
        super(TypeMapper, self).__init__(fget, fset, fdel)
        self.nonable = nonable

    def buildGetter(self, obj):
        @functools.wraps(self.fget)
        def _wrapper(*args, **kwargs):
            untyped = self.fget(*args, **kwargs)
            try:
                rv = self.typeFrom(untyped)
            except TypeError:
                if (untyped is None) and self.nonable:
                    rv = untyped
                else:
                    raise
            return rv
        return base.SourceTrail(obj, _wrapper)

    def _doSet(self, obj, value):
        super(TypeMapper, self)._doSet(obj, self.typeTo(value))

class SourceStr(TypeMapper):
    pass

class SourceInt(TypeMapper):

    typeFrom = int

class OnOff(TypeMapper):

    def typeFrom(self, value):
        value = value.lower()
        assert value in ("on", "off")
        return value == "on"

    def typeTo(self, value):
        return "on" if value else "off"