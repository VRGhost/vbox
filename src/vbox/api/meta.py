import collections
import pickle

from . import base

class MetaDict(collections.MutableMapping):

    def __init__(self, data, changeCb):
        super(MetaDict, self).__init__()
        self._changeCb = changeCb
        self._data = data

    def __getitem__(self, name):
        rv = self._data[name]
        if isinstance(rv, collections.MutableMapping):
            rv = self.__class__(rv, lambda el: self._onChange(name))
        return rv

    def __setitem__(self, name, value):
        self._data[name] = value
        self._onChange(name)

    def __delitem__(self, name):
        del self._data[name]
        self._onChange(name)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _onChange(self, name):
        self._changeCb(self)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self._data)

class MetaSession(MetaDict):

    def __init__(self, *args, **kwargs):
        super(MetaSession, self).__init__(*args, **kwargs)
        self._pending = set()

    def _onChange(self, name):
        self._pending.add(name)

    def __enter__(self):
        self._pending.clear()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (exc_type, exc_value, traceback) == (None, ) * 3:
            # No exceptions.
            if self._pending:
                self._changeCb(self, self._data, self._pending)

class Meta(base.SourceObjectProxy, collections.MutableMapping):

    picklePrefix = "(py_vbox_pickle)"

    def __getitem__(self, key):
        rv = self.source.get(key)
        if rv.startswith(self.picklePrefix):
            strVal = rv[len(self.picklePrefix):]
            rv = pickle.loads(strVal.decode("base64").decode("zip"))
            if isinstance(rv, collections.MutableMapping):
                rv = MetaDict(rv, lambda obj: self._onDictChanged(key, obj))
        return rv

    def __setitem__(self, key, value):
        try:
            oldValue = self[key]
        except KeyError:
            pass
        else:
            # oldValue present
            if oldValue == value:
                return
                
        value = self._stripMetaDict(value)
        strValue = pickle.dumps(value, pickle.HIGHEST_PROTOCOL).encode("zip").encode("base64")
        strValue = "".join(strValue.split())
        self.source.set(key, self.picklePrefix + strValue)

    def __delitem__(self, key):
        self.source.rm(key)

    def __iter__(self):
        return iter(self.source.keys())

    def __len__(self):
        return len(self.source.keys())

    def _onDictChanged(self, key, value):
        self[key] = value

    def _stripMetaDict(self, value):
        strip = self._stripMetaDict

        if isinstance(value, MetaDict):
            value = dict(value)

        if isinstance(value, dict):
            rv = dict((strip(key), strip(value)) for (key, value) in value.items())
        elif isinstance(value, (list, tuple)):
            rv = value.__class__(strip(el) for el in value)
        else:
            rv = value

        return rv

    def _sessionCommit(self, obj, data, changed):
        for name in changed:
            value = data[name]
            self[name] = value

    def session(self):
        """Return context object that commits all pending changes to the controlled MutableMapping on the context __exit__."""
        return MetaSession(self, self._sessionCommit)