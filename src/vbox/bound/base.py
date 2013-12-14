import collections
import functools
import sys
import threading

from ..exceptions import ExceptionCatcher
from . import exceptions

import vbox.base

_EMPTY_ = object()

class Caching(vbox.base.Cacher):

    exceptions = exceptions

class BoundCaching(Caching):
    """A caching object that is bound to another object that it passes as 'self' to the function it is controlling."""

    def __init__(self, backendFn, obj, maxCacheAge=None):
        super(BoundCaching, self).__init__(backendFn, maxCacheAge=maxCacheAge)
        self.boundTo = obj
        obj.addSubscriber(self)

    def _doRealCall(self, args, kwargs):
        boundArgs = [self.boundTo]
        boundArgs.extend(args)
        return super(BoundCaching, self)._doRealCall(boundArgs, kwargs)

@vbox.base.decorators.parametricDecorator
def refreshed(func, maxCacheAge=None):
    """A bound caching function that is refreshed via 'refreshCallbacks' mechanism."""
    return vbox.base.decorators.BindingDescriptor(
        lambda self: BoundCaching(func, self, maxCacheAge=maxCacheAge)
    )

@vbox.base.decorators.parametricDecorator
def refreshedProperty(func, **kwargs):
    handle = refreshed(func, **kwargs)
    fn1 = lambda self: handle.getBoundObject(self)()
    fn2 = functools.wraps(handle)(fn1)
    return property(fn2)

class Refreshable(vbox.base.CacheChain):
    """An object that can uses caching and thus can be refreshed."""

    exceptions = exceptions


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
        self.root.addSubscriber(self)

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
        for el in self.all():
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

    def __init__(self, library, id):
        super(Entity, self).__init__(library.root.cli)
        self.id = id
        self.library = library
        self.root = library.root
        self.library.addSubscriber(self)

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