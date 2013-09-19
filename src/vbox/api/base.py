import threading

class SourceObjectProxy(object):

    _source = _sourceDependants = None

    def __init__(self, sourceObject):
        super(SourceObjectProxy, self).__init__()
        self._sourceDependants = set()
        self._source = sourceObject
        self._source.addRefreshCallback(self._onSourceRefresh)

    def _onSourceRefresh(self):
        for el in self._sourceDependants:
            el.refresh()

class SourceTrail(object):
    """Function whose result is dependant on the internal state of the source object
    """

    _func = version = None

    def __init__(self, bound, func):
        super(SourceTrail, self).__init__()
        assert callable(func)
        self._func = func
        self._parent = bound
        self._cacheLock = threading.Lock()


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
        return self._func(self._parent._source)

    def refresh(self):
        with self._cacheLock:
            try:
                del self._cache
            except AttributeError:
                pass

    def __repr__(self):
        return "<{}({!r})>".format(self.__class__.__name__, self._func)

class Entity(SourceObjectProxy):
    pass

class Library(SourceObjectProxy):

    entityCls = None # class for the entities this library produces

    def __init__(self, sourceObject, interface):
        super(Library, self).__init__(sourceObject)
        self._interface = interface