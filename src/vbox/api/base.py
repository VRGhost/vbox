from collections import defaultdict

class Base(object):
    """Base class for API objects."""

    kwargName = None
    expectedKwargs = None # Replace with dict in child classes!

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__()
        realKwargs = defaultdict(list)

        for (name, el) in kwargs.iteritems():
            self._constructKwargs(realKwargs, el, name)

        for el in args:
            self._constructKwargs(realKwargs, el)

        realKwargs = dict((name, tuple(value)) for (name, value) in realKwargs.iteritems())
        # Ensure that all kwargs mentioned in the `expectedKwargs`
        # are actually initialised in `realKwargs`
        for name in self.expectedKwargs.keys():
            realKwargs[name]  = ()

        self._verifyKwargs(realKwargs)
        self._initObject(realKwargs)

    def _initObject(self, kwargs):
        """Actual object-dependant kwarg handler."""
        # Children classes should override this function for custom functionality
        for (name, value) in kwargs.iteritems():
            isOk = self._getAllowedFn(name)
            if (len(value) <= 1) and (not isOk(2)):
                # Assume that this is single object
                if len(value) == 1:
                    value = value[0]
                else:
                    value = None
            setattr(self, name, value)


    def _verifyKwargs(self, obj):
        for (name, lst) in obj.iteritems():
            allowed = self._getAllowedFn(name)
            if not allowed(len(lst)):
                raise ValueError("{!r} is not expected to get {} values.".format(name, len(lst)))

    def _getAllowedFn(self, name):
        try:
            rv = self.expectedKwargs[name]
        except KeyError:
            rv = lambda lstLen: False

        if not callable(rv):
            rv = lambda lstLen: lstLen == rv
        return rv


    def _constructKwargs(self, out, obj, name=None):
        isContainer = lambda el: isinstance(el, (list, tuple))

        if isContainer(obj):
            for el in obj:
                self._constructKwargs(out, el, name)
        else:
            # Not a container type
            if not name:
                name = obj.kwargName

            out[name].append(obj)

# Predefined library of common parameter validators.
expects = object()
expects.__dict__.update({
    "any" : lambda len: True,
})