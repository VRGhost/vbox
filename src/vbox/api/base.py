import threading


import vbox.base

from ..exceptions import ExceptionCatcher
from . import exceptions

class SourceObjectProxy(vbox.base.CacheChain):

    exceptions = exceptions
    _source = _sourceDependants = None
    source = property(lambda s: s._source)

    def __init__(self, sourceObject):
        super(SourceObjectProxy, self).__init__()
        self._cacheClearDependants = set()
        self._sourceCacheUpdateDependants = set()
        self._source = ExceptionCatcher(sourceObject, self._onSourceException)
        self.source.addSubscriber(self)

    def _onSourceException(self, exc):
        """Called when source call raises an exception."""

    def __eq__(self, other):
        try:
            src2 = other.source
        except AttributeError:
            return False
        return self.source.is_(src2)

    def __repr__(self):
        return "<{}.{} 0x{:X} {!r}>".format(self.__module__, self.__class__.__name__, id(self), self.source)

class ProxyRefreshTrail(vbox.base.Cacher):
    """Function that caches its result and resets its cache when any of source objects are refreshed.
    """

    def __init__(self, func, depends=()):
        super(ProxyRefreshTrail, self).__init__(func)
        assert callable(func)
        assert depends, "Must define at least one source. Provided: {}".format(depends)
        self.depends = tuple(depends)
        for el in self.depends:
            el.addSubscriber(self)

    def onCacheUpdate(self, who):
        super(ProxyRefreshTrail, self).onCacheUpdate(who)
        if who in self.depends:
            self.clearCache()

class Entity(SourceObjectProxy):


    def __init__(self, sourceObject, library):
        super(Entity, self).__init__(sourceObject)
        self.library = library
        self.interface = library.interface

class Library(SourceObjectProxy):

    entityCls = None # class for the entities this library produces

    def __init__(self, sourceObject, interface):
        super(Library, self).__init__(sourceObject)
        self.interface = interface

    def isRegistered(self, apiObject):
        assert apiObject.library is self, (apiObject, self)
        return self.source.isRegistered(apiObject.source)

    def listRegistered(self):
        return tuple(self.entityCls(src, self) for src in self.source.listRegistered())

class SubEntity(SourceObjectProxy):

    def __init__(self, parent):
        super(SubEntity, self).__init__(parent.source)
        self.parent = parent
        self.interface = parent.interface