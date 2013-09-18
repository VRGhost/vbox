import collections
import copy
import functools
import sys

_EMPTY_ = object()

CallArgs = collections.namedtuple("CallArgs", ["args", "kwargs"])
MAX_VERSION = sys.maxint

class Caching(object):
    """Base API object that provided caching primitives.

    Important public fields:
        `version` - contains ID of the current version of the contents. Allows for external object to peek into the expected return value of
            this object: will it be the same (`version` field unchanged) or can be different (`version` field changed).

    """

    _backendFn = version = _cache = None

    def __init__(self, backendFn):
        super(Caching, self).__init__()
        self._cache = {}

        assert callable(backendFn)
        self._backendFn = backendFn
        self.version = 1

    def __call__(self, *args, **kwargs):
        key = CallArgs(tuple(args), frozenset(kwargs.items()))
        try:
            rv = self._cache[key]
        except KeyError:
            self._cache[key] = self._backendFn(*args, **kwargs)
            rv = self._cache[key]

        return copy.deepcopy(rv)


    def refresh(self):
        self.version += 1
        if self.version >= MAX_VERSION:
            # Rollover!
            self.version = 1

        self._cache.clear()

class Library(object):
    """An object factory."""

    entityCls = None # Entity class that this library generates.
    root = objects = None

    def __init__(self, root):
        super(Library, self).__init__()
        self.root = root
        self.objects = []

    def listRegistered(self):
        """Return all objects of this type that VirtualBox has present in its registry."""
        raise NotImplementedError

    def all(self):
        """Return all objects that are known of by now."""
        return iter(self.objects)

    def pop(self, challange):
        """Remove and return object described."""
        for el in self.objects:
            if el.is_(challange):
                found = el
                break
        else:
            raise IndexError(challange)
        self.objects.remove(el)
        return el

    def new(self, idx):
        if idx in self:
            raise KeyError("{!r} already exists".format(idx))
        rv = self.entityCls(self, idx)
        self.objects.append(rv)
        return rv

    def __contains__(self, challange):
        for el in self.objects:
            if el.is_(challange):
                return True
        else:
            return False

class Entity(object):
    """Single entity (produced by the factory)."""

    def __init__(self, library, id):
        super(Entity, self).__init__()

        self.id = id

        self.library = library
        self.root = library.root
        self.cli = self.root.cli

    def is_(self, challange):
        """Return 'True' is this object is the one that is hiding under 'challange'."""
        return (challange is self) or (self.id == challange)


    def refresh(self):
        """Order a refresh all cached properties of this object."""

    def __repr__(self):
        return "<{} {!r} of {!r}>".format(self.__class__.__name__, self.id, self.library)

def refreshing(func):
    """function upon competion of which 'refresh' for current object will be called."""
    def _wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            self.refresh()
    return functools.wraps(func)(_wrapper)