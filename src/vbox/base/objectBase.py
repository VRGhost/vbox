import threading
import collections
import sys
import weakref

MAX_VERSION = sys.maxint

class CacheChain(object):
    """Object that does not implement caching of its own,

    But is is able to hold any number of caching event subscribers
    and to forward events passed to itself to its subscribers.
    """

    _subscribers = None

    def __init__(self):
        super(CacheChain, self).__init__()
        self._subscribers = []

    def addSubscriber(self, obj):
        self._subscribers.append(weakref.ref(obj))

    def clearCache(self):
        """An order for this object to clear its cache."""
        for sub in self._iterSubscribers():
            sub.clearCache()

    def onCacheUpdate(self, who):
        """An event callback that tells this object that
        another object had cleared its cache.
        """
        for sub in self._iterSubscribers():
            sub.onCacheUpdate(who)

    def onTimeTick(self, period):
        for sub in self._iterSubscribers():
            sub.onTimeTick(period)

    def _iterSubscribers(self):
        toRemove = []
        for ref in self._subscribers:
            target = ref()
            if target is None:
                toRemove.append(ref)
            else:
                yield target
        
        for ref in toRemove:
            self._subscribers.remove(ref)

    def __repr__(self):
        return "<{}.{} {:X}>".format(
            self.__module__, self.__class__.__name__,
            id(self)
        )

class _CachedResult(object):

    def __init__(self, result, ttl=None):
        super(_CachedResult, self).__init__()
        self.result = result
        self.ttl = ttl

    @classmethod
    def getKey(cls, args, kwargs):
        return (
            tuple(args),
            frozenset(kwargs.items()),
        )

    def __repr__(self):
        return "<{} ttl={} result={!r}>".format(
            self.__class__.__name__,
            self.ttl, self.result,
        )

class Cacher(CacheChain):
    """Base API object that provided caching primitives.

    Important public fields:
        `version` - contains ID of the current version of the contents. Allows for external object to peek into the expected return value of
            this object: will it be the same (`version` field unchanged) or can be different (`version` field changed).

    """

    _backendFunc = _cacheLock = _cache = None

    def __init__(self, backendFn, maxCacheAge=float("inf")):
        super(Cacher, self).__init__()
        assert callable(backendFn)
        self.maxCacheAge = maxCacheAge
        self._backendFunc = backendFn
        self.version = 1
        self._cacheLock = threading.RLock()
        self._cache = {}

        try:
            addDep = backendFn.addSubscriber
        except AttributeError:
            pass
        else:
            addDep(self)

    def clearCache(self):
        with self._cacheLock:
            self._cache.clear()
            super(Cacher, self).clearCache()

    def onTimeTick(self, period):
        """Remember that time ticks are executed in a separate thread."""

        super(Cacher, self).onTimeTick(period)
        with self._cacheLock:
            toExpire = []

            for (key, result) in self._cache.iteritems():
                if result.ttl > 0:
                    result.ttl -= period

                if result.ttl <= 0:
                    toExpire.append(key)

            if toExpire:
                for key in toExpire:
                    del self._cache[key]
                # leave a message to a main thread so it can raise 'onCacheUpdate' message
                self.onCacheUpdate(self)

    def __call__(self, *args, **kwargs):
        return self._callHandle(args, kwargs)

    def _callHandle(self, args, kwargs):
        key = _CachedResult.getKey(args, kwargs)
        try:
            value = self._getCached(key)
        except KeyError as err:
            with self._cacheLock:
                # Try reading cache once again - somebody might have changed it.
                try:
                    value = self._getCached(key)
                except KeyError as err:
                    value = self._cache[key] = _CachedResult(
                        self._doRealCall(args, kwargs),
                        ttl=self.maxCacheAge,
                    )
                    self.onCacheUpdate(self)
        return value.result

    def _getCached(self, key):
        """Return cached result. Raises KeyError if not found."""
        return self._cache[key]

    def _doRealCall(self, args, kwargs):
        return self._backendFunc(*args, **kwargs)

    def __repr__(self):
        return "<{}.{}({!r})>".format(
            self.__module__, self.__class__.__name__,
            self._backendFunc
        )
