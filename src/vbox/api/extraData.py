import binascii
import pickle
import collections

_NULL = object()

class AutoPicklingDict(collections.MutableMapping):

    _data = cb = None

    def __init__(self):
        super(AutoPicklingDict, self).__init__()
        self._data = {}

    def update(self, vals):
        for (name, value) in vals.iteritems():
            self[name] = value

    def __getitem__(self, name):
        return self._data[name]

    def __setitem__(self, name, value):
        if isinstance(value, collections.MutableMapping):
            if isinstance(value, AutoPicklingDict):
                newVal = value
            else:
                newVal = self.fromDict(value)
            newVal.setOnChangeCallback(self._onChildUpdate)
            value = newVal
        self._data[name] = value
        if self.cb:
            self.cb(self, name, value)

    def __delitem__(self, name):
        del self._data[name]

    def __iter__(self):
        return self._data.iterkeys()

    def __len__(self):
        return len(self._data)


    def _onChildUpdate(self, child, name, value):
        if self.cb:
            for (name, value) in self._data.iteritems():
                if value == child:
                    key = value
                    break
            else:
                raise KeyError(value)
            self.cb(self, key, child)

    def setOnChangeCallback(self, callback):
        if self.cb is not None:
            raise Exception("Callback is already set.")
        self.cb = callback

    @classmethod
    def fromDict(cls, dict):
        obj = cls()
        obj.update(dict)
        return obj

    # Pickling protocol follow
    def __getstate__(self):
        return self._data

    def __setstate__(self, state):
        # ! remember that __init__ is not called when unpickling!
        self._data = {}
        self.update(state)

    def __repr__(self):
        return "<{} {!r}>".format(
            self.__class__.__name__, self._data)

class ExtraData(object):
    """VM extra data accessor with pickling."""

    def __init__(self, vm):
        self.vm = vm
        self.pyObj = vm.pyVm.extraData

    def get(self, name, default=None):
        return self.cache.get(name, default)

    def set(self, name, value):
        self.pyObj.setProp(self._encode(name), self._encode(value))
        del self.cache

    def __getitem__(self, name):
        rv = self.get(name, _NULL)
        if rv is _NULL:
            raise KeyError(name)
        return rv

    def __setitem__(self, name, value):
        self.set(name, self._ensurePicklingDict(value, name))

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.cache)

    def __iter__(self):
        return self.cache.iterkeys()

    def _reCache(self):
        out = {}
        source = self.pyObj.info
        if source:
            for (name, value) in source.iteritems():
                key = self._decode(name)
                pyObj = self._decode(value)
                pyObj = self._ensurePicklingDict(pyObj, key)
                out[key] = pyObj
        return out

    def _ensurePicklingDict(self, obj, cbKey):
        if isinstance(obj, collections.MutableMapping):
            if isinstance(obj, AutoPicklingDict):
                rv = obj
            else:
                rv = AutoPicklingDict.fromDict(obj)
            rv.setOnChangeCallback(
                lambda setObj, objKey, objVal: self.set(cbKey, setObj))
        else:
            rv = obj
        return rv

    def _decode(self, value):
        try:
            unarch = value.decode("base64").decode("zip")
        except Exception:
            return value
        return pickle.loads(unarch)

    def _encode(self, value):
        return pickle.dumps(value, pickle.HIGHEST_PROTOCOL).encode("zip").encode("base64").replace('\n', '')

    _cache = _cacheSignature = None
    @property
    def cache(self):
        _newSign = repr(self.pyObj.info)
        if (self._cacheSignature != _newSign) or (not self._cache):
            self._cache = self._reCache()
            self._cacheSignature = _newSign
        return self._cache

    @cache.deleter
    def cache(self):
        self._cacheSignature = None
        self._cache = None
