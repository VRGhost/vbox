"""Utility functions."""

def boundProperty(fn):
    origFnName = fn.func_name
    cacheName = "__cached{}_at_0x{:x}_Value".format(origFnName, id(fn))
    def _bounder(self):
        try:
            return getattr(self, cacheName)
        except AttributeError:
            rv = fn(self)
            if rv is not None:
                setattr(self, cacheName, rv)
            return rv
    return property(_bounder)