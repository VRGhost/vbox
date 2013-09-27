import collections
import pickle

from . import base

class Meta(base.SourceObjectProxy, collections.MutableMapping):

    picklePrefix = "(py_vbox_pickle)"

    def __getitem__(self, key):
        rv = self.source.get(key)
        if rv.startswith(self.picklePrefix):
            strVal = rv[len(self.picklePrefix):]
            rv = pickle.loads(strVal.decode("base64").decode("zip"))
        return rv

    def __setitem__(self, key, value):
        strValue = pickle.dumps(value, pickle.HIGHEST_PROTOCOL).encode("zip").encode("base64")
        strValue = "".join(strValue.split())
        self.source.set(key, self.picklePrefix + strValue)

    def __delitem__(self, key):
        self.source.rm(key)

    def __iter__(self):
        return iter(self.source.keys())

    def __len__(self):
        return len(self.source.keys())