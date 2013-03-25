import binascii
import pickle

_NULL = object()

class ExtraData(object):
    """VM extra data accessor with pickling."""

    def __init__(self, vm):
        self.vm = vm
        self.pyObj = vm.pyVm.extraData

    def get(self, name, default=None):
        rv = self.pyObj.getProp(name, default)
        rv = pickle.loads(rv)
        return rv

    def set(self, name, value):
        self.pyObj.setProp(self._encode(name), self._encode(value))

    def __getitem__(self, name):
        rv = self.get(name, _NULL)
        if rv is _NULL:
            raise KeyError(name)
        return rv

    def __setitem__(self, name, value):
        self.set(name, value)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.cache)

    def _reCache(self):
        out = {}
        for (name, value) in self.pyObj.info.iteritems():
            out[self._decode(name)] = self._decode(value)
        return out

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
        if self._cacheSignature != _newSign:
            self._cache = self._reCache()
            self._cacheSignature = _newSign
        return self._cache
