import threading
import collections
import sys

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
        self._subscribers.append(obj)

    def clearCache(self):
        """An order for this object to clear its cache."""

        for sub in self._subscribers:
            sub.clearCache()

    def onCacheUpdate(self, who):
        """An event callback that tells this object that
        another object had cleared its cache.
        """
        for sub in self._subscribers:
            sub.onCacheUpdate(who)

    def onTimeTick(self, period):
        for sub in self._subscribers:
            sub.onTimeTick(period)

    def __repr__(self):
        return "<{}.{} {:X}>".format(
            self.__module__, self.__class__.__name__,
            id(self)
        )

class _CachedResult(object):

    def __init__(self, args, kwargs, result, ttl=None):
        super(_CachedResult, self).__init__()
        self.key = self.getKey(args, kwargs)
        self.result = result
        self.ttl = ttl

    @classmethod
    def getKey(cls, args, kwargs):
        return (
            tuple(args),
            frozenset(kwargs.items()),
        )

class Cacher(CacheChain):
    """Base API object that provided caching primitives.

    Important public fields:
        `version` - contains ID of the current version of the contents. Allows for external object to peek into the expected return value of
            this object: will it be the same (`version` field unchanged) or can be different (`version` field changed).

    """

    _backendFunc = _cacheLock = _cache = None

    def __init__(self, backendFn):
        super(Cacher, self).__init__()
        assert callable(backendFn)
        self._backendFunc = backendFn
        self.version = 1
        self._cacheLock = threading.Lock()
        self._cache = {}

    def clearCache(self):
        with self._cacheLock:
            self._cache.clear()
            super(Cacher, self).clearCache()

    def __call__(self, *args, **kwargs):
        return self._callHandle(args, kwargs)

    def _callHandle(self, args, kwargs):
        key = _CachedResult.getKey(args, kwargs)
        try:
            value = self._cache[key]
        except KeyError:
            with self._cacheLock:
                # Try reading cache once again - somebody might have changed it.
                try:
                    value = self._cache[key]
                except KeyError:
                    value = self._cache[key] = self._doRealCall(args, kwargs)
        return value.result

    def _doRealCall(self, args, kwargs):
        result = self._backendFunc(*args, **kwargs)
        return _CachedResult(
            args, kwargs,
            result,
        )

    def __repr__(self):
        return "<{}.{}({!r})>".format(
            self.__module__, self.__class__.__name__,
            self._backendFunc
        )
