import threading

class SourceObjectProxy(object):

    _source = _sourceDependants = None
    source = property(lambda s: s._source)

    def __init__(self, sourceObject):
        super(SourceObjectProxy, self).__init__()
        self._cacheClearDependants = set()
        self._sourceCacheUpdateDependants = set()
        self._source = sourceObject
        self.source.addCacheClearCallback(self._onSourceCacheClear)
        self.source.addCacheUpdateCallback(self._onSourceCacheUpdate)

    def addCacheClearCallback(self, func):
        self._cacheClearDependants.add(func)

    def addCacheUpdateCallback(self, func):
        self._sourceCacheUpdateDependants.add(func)

    def clearCache(self, src):
        assert src == self.source
        for el in self._cacheClearDependants:
            el(self)

    def _onSourceCacheClear(self, src):
        assert src == self.source
        self.clearCache(src)

    def _onSourceCacheUpdate(self, src):
        assert src == self.source
        for el in self._sourceDependants:
            el.cacheUpdated(src)

    def registerTrail(self, dep):
        self.addCacheClearCallback(dep.clearCache)

class ProxyRefreshTrail(object):
    """Function that caches its result and resets its cache when any of source objects are refreshed.
    """

    _func = version = None

    def __init__(self, func, depends=()):
        super(ProxyRefreshTrail, self).__init__()
        assert callable(func)
        self._func = func
        self._cacheLock = threading.Lock()
        assert depends, "Must define at least one source. Provided: {}".format(depends)
        for el in depends:
            el.registerTrail(self)


    def __call__(self):
        return self._callHandle()

    def _callHandle(self):
        try:
            return self._cache
        except AttributeError:
            with self._cacheLock:
                # Trye reading cache once again - somebody might have changed it.
                try:
                    return self._cache
                except AttributeError:
                    self._cache = self._doRealCall()
                    return self._cache

    def _doRealCall(self):
        return self._func()

    def clearCache(self, src):
        with self._cacheLock:
            try:
                del self._cache
            except AttributeError:
                pass

    def __repr__(self):
        return "<{}({!r})>".format(self.__class__.__name__, self._func)

class Entity(SourceObjectProxy):
    

    def __init__(self, sourceObject, library):
        super(Entity, self).__init__(sourceObject)
        self.library = library

class Library(SourceObjectProxy):

    entityCls = None # class for the entities this library produces

    def __init__(self, sourceObject, interface):
        super(Library, self).__init__(sourceObject)
        self.interface = interface

    def isRegistered(self, apiObject):
        assert apiObject.library is self, (apiObject, self)
        return self.source.isRegistered(apiObject.source)

class SubEntity(SourceObjectProxy):

    def __init__(self, parent):
        super(SubEntity, self).__init__(parent.source)
        self.parent = parent