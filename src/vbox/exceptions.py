class BaseException(Exception):
    """Base class for all exceptions in the project."""

class VirtualBoxNotFound(BaseException):
    """Virtualbox executable not found."""


class ExceptionCatcher(object):
    """Object that proxies another object and forwards all exceptions that arise during the call to the exception handling function.

    Only custom `BaseException`-base exceptions are caught.

    If the callback does not rais any exception and returns `False`, the original exception is re-reaised.
    """

    def __init__(self, proxy, callback, excClass=BaseException):
        self._proxy = proxy
        self._cb = callback
        self._targetCls = excClass
        assert callable(self._cb)

    def __call__(self, *args, **kwargs):
        try:
            return self._proxy(*args, **kwargs)
        except self._targetCls as err:
            if not self._cb(err):
                raise

    def __getattr__(self, name):
        rv = getattr(self._proxy, name)
        if callable(rv):
            cls = self.__class__
            rv = cls(rv, self._cb, self._targetCls)
            setattr(self, name, rv)
        return rv


    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self._proxy)