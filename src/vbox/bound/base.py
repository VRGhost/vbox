import collections
import functools
import sys
import threading

from ..exceptions import ExceptionCatcher
from . import exceptions

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
        self._cacheLock = threading.Lock()

    def __call__(self, *args, **kwargs):
        return self._callHandle(args, kwargs)

    def _callHandle(self, args, kwargs):
        key = CallArgs(tuple(args), frozenset(kwargs.items()))
        try:
            value = self._cache[key]
        except KeyError:
            with self._cacheLock:
                # Trye reading cache once again - somebody might have changed it.
                try:
                    value = self._cache[key]
                except KeyError:
                    value = self._cache[key] = self._doRealCall(args, kwargs)
        return value

    def _doRealCall(self, args, kwargs):
        return self._backendFn(*args, **kwargs)

    def clearCache(self):
        self.version += 1
        if self.version >= MAX_VERSION:
            # Rollover!
            self.version = 1
        with self._cacheLock:
            self._cache.clear()

    def __repr__(self):
        return "<{}({!r})>".format(self.__class__.__name__, self._backendFn)

class BoundCaching(Caching):
    """A caching object that is bound to another object that it passes as 'self' to the function it is controlling."""

    def __init__(self, backendFn, obj):
        super(BoundCaching, self).__init__(backendFn)
        self.boundTo = obj

    def _callHandle(self, args, kwargs):
        boundArgs = [self.boundTo]
        boundArgs.extend(args)
        return super(BoundCaching, self)._callHandle(boundArgs, kwargs)

    def __repr__(self):
        return "<{}({!r}.{!r})>".format(self.__class__.__name__, self.boundTo, self._backendFn)

def refreshed(func):
    """A bound caching function that is refreshed via 'refreshCallbacks' mechanism."""
    name = "_refreshed_cache_for_{!r}".format(func.__name__)
    def _wrapper(self, *args, **kwargs):
        try:
            handler = self.__dict__[name]
        except KeyError:
            handler = BoundCaching(func, self)
            self.addCacheClearCallback(lambda s: handler.clearCache())
            self.__dict__[name] = handler # This will effectivly prohibit successive '_wrapper' calls and will force for 'handler' to be called instead.
            
        return handler(*args, **kwargs)
    return functools.wraps(func)(_wrapper)

def refreshedProperty(func):
    handle = refreshed(func)
    fn1 = lambda self: handle(self)
    fn2 = functools.wraps(handle)(fn1)
    return property(fn2)

class Refreshable(object):
    """An object that can uses caching and thus can be refreshed."""

    refreshCallbacks = None

    def __init__(self):
        super(Refreshable, self).__init__()
        self.cacheClearCallbacks = []
        self.cacheUpdateCallbacks = []

    def addCacheClearCallback(self, cb):
        self.cacheClearCallbacks.append(cb)

    def addCacheUpdateCallback(self, cb):
        self.cacheUpdateCallbacks.append(cb)

    def clearCache(self):
        self.onCacheClear()

    def onCacheClear(self):
        """Order a refresh all cached properties of this object."""
        for cb in self.cacheClearCallbacks:
            cb(self)

    def onCacheUpdate(self):
        """Order a refresh all cached properties of this object."""
        for cb in self.cacheUpdateCallbacks:
            cb(self)

    def __repr__(self):
        return "<{}.{} {:X}>".format(self.__module__, self.__class__.__name__, id(self))


class CliAccessor(Refreshable):

    def __init__(self, cli):
        super(CliAccessor, self).__init__()
        self.cli = ExceptionCatcher(cli, self.onCliCallError)

    def cliCall(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except self.cli.exceptions.CalledProcessError as err:
            self.onCliCallError(err)

    def onCliCallError(self, err):
        raise


class Library(CliAccessor):
    """An object factory."""

    entityCls = None # Entity class that this library generates.
    root = objects = cli = None
    exceptions = exceptions

    def __init__(self, root):
        super(Library, self).__init__(root.cli)
        self.root = root
        self.objects = []

    def listRegistered(self):
        """Return all objects of this type that VirtualBox has present in its registry."""
        raise NotImplementedError

    def isRegistered(self, challange):
        for el in self.listRegistered():
            if el.is_(challange):
                return True
        return False

    def all(self):
        """Return all objects that are known of by now."""
        return iter(self.objects)

    def new(self, idx):
        rv = self.entityCls(self, idx)
        return self.dedup(rv)

    def dedup(self, obj):
        try:
            # If 'get' call suceeds, there is an object that matches `obj`
            rv = self.get(obj)
        except IndexError:
            self.objects.append(obj)
            rv = obj
        return rv

    def get(self, challange):
        for el in self.objects:
            if el.is_(challange):
                return el
        else:
            raise IndexError(challange)

    def pop(self, challange):
        """Remove and return object described."""
        el = self.get(challange)
        self.objects.remove(el)
        return el

    def getOrCreate(self, idx):
        try:
            return self.get(idx)
        except IndexError:
            return self.new(idx)

    def __contains__(self, challange):
        for el in self.objects:
            if el.is_(challange):
                return True
        else:
            return False

class Entity(CliAccessor):
    """Single entity (produced by the factory)."""
    exceptions = exceptions

    def __init__(self, library, id):
        super(Entity, self).__init__(library.root.cli)
        self.id = id
        self.library = library
        self.root = library.root

    def is_(self, challange):
        """Return 'True' is this object is the one that is hiding under 'challange'."""
        if (challange is self) or (self.id == challange):
            return True
        try:
            id2 = challange.id
        except AttributeError:
            pass
        else:
            if self.id == id2:
                return True

        return False


    def __repr__(self):
        return "<{}.{} {!r} of {!r}>".format(self.__module__, self.__class__.__name__, self.id, self.library)

def refreshing(func):
    """function upon competion of which 'refresh' for current object will be called."""
    def _wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            self.clearCache()
    return functools.wraps(func)(_wrapper)

def refreshingLib(func):

    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            self.library.clearCache()

    return refreshing(_wrapper)