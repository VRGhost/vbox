from collections import defaultdict

class Base(object):
    """Base class for API objects."""

    kwargName = None
    initOrder = () # Order at which kwargs are going to be applied
    expectedKwargs = None # Replace with dict in child classes!
    defaultKwargs = None
    boundKwargs = None

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__()
        realKwargs = defaultdict(list)

        for (name, el) in kwargs.iteritems():
            self._constructKwargs(realKwargs, el, name)

        for el in args:
            self._constructKwargs(realKwargs, el)

        boundKwargs = dict((name, tuple(value)) for (name, value) in realKwargs.iteritems())
        # Ensure that all kwargs mentioned in the `expectedKwargs`
        # are actually initialised in `realKwargs`
        for name in self.expectedKwargs.keys():
            if name not in boundKwargs:
                boundKwargs[name]  = ()

        self._verifyKwargs(boundKwargs)
        boundKwargs = self._flatternLayout(boundKwargs)
        self._setup(boundKwargs)
        self.boundKwargs = boundKwargs
        self._init()

    def _flatternLayout(self, kwargs):
        out = {}
        for (key, value) in kwargs.iteritems():
            isOk = self._getAllowedFn(key)
            if (len(value) <= 1) and (not isOk(2)):
                # Assume that this is single object
                if len(value) == 1:
                    value = value[0]
                else:
                    valueCb = self.defaultKwargs.get(key)
                
                    if valueCb is None:
                        # Do not init given property at all
                        continue
                    value = valueCb()
            out[key] = value
        return out

    def _setup(self, kwargs):
        """Actual object-dependant kwarg handler."""
        # Children classes should override this function for custom functionality
        kwargOrder = list(self.initOrder)
        extraNames = [name for name in kwargs.iterkeys() if name not in kwargOrder]
        # Unmentioned kwarg names are to be initialised last.
        kwargOrder.extend(extraNames)

        for name in kwargOrder:
            value = kwargs[name]
            self.setProp(name, value)
            self._registerAsParent(value)

    def setProp(self, name, value):
        setattr(self, name, value)

    def _registerAsParent(self, child):
        def _setParentCb(obj):
            try:
                cb = obj.setParent
            except AttributeError:
                pass
            else:
                cb(self)

        if  isinstance(child, tuple):
            it = child
        else:
            it = (child, )

        for el in it:
            _setParentCb(el)

    def _init(self):
        """Custom initialisation function."""


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
            def _mkBoundFn(cnt):
                if isinstance(cnt, (list, tuple)):
                    rv = lambda lstLen: lstLen in cnt
                else:
                    rv = lambda lstLen: lstLen == cnt
                return rv
            rv = _mkBoundFn(rv)
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
            assert isinstance(name, basestring), name
            out[name].append(obj)

    def __repr__(self):
        out = []
        for name in self.expectedKwargs.keys():
            try:
                val = getattr(self, name)
            except AttributeError:
                val = "!NO ARG!"
            out.append("{}={!r}".format(name, val))
        return "<{} {!r} {}>".format(self.__class__.__name__, self.kwargName, " ".join(out))

class Child(Base):

    _parent = _kwargStore = None
    parent = property(lambda s: s._parent)
    pyVm = property(lambda s: s.parent.pyVm)
    pyVb = property(lambda s: s.parent.pyVb)

    def setParent(self, parent):
        if self._parent is not None:
            raise Exception("Parent already set")
        self._parent = parent
        # Re-call setup to apply actual changes.
        self._setup(self.boundKwargs)

    def _setup(self, kwargs):
        if self._relationshipsConfigured():
            self.befoureSetup(kwargs)
            super(Child, self)._setup(kwargs)
            self.afterSetup(kwargs)

    def befoureSetup(self, kwargs):
        pass

    def afterSetup(self, kwargs):
        pass

    def _relationshipsConfigured(self):
        """Return `True` if this object can reach all essential API functions."""
        return (self._parent is not None) and (self.pyVm is not None)

def pyVmProp(name):
    """Bound property of pyVm."""
    def pyVmProp_fset(self, value):
        setattr(self.pyVm, name, value)
    def pyVmProp_fget(self):
        return getattr(self.pyVm, name)
    return property(pyVmProp_fget, pyVmProp_fset)