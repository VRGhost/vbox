class ParametricDecorator(object):

    _subjectFunction = _decorationFunction = _kwargs = None

    def __init__(self, target):
        super(ParametricDecorator, self).__init__()
        assert callable(target)
        self._decorationFunction = target
        self._kwargs = {}

    def __call__(self, *args, **kwargs):
        if (not args) and (not kwargs):
            raise NotImplementedError("No parameters passed.")

        if args and kwargs:
            # No not store kwargs passed in this call,
            # so they affect only decoration of the current function
            opKwargs = self._kwargs.copy()
        else:
            opKwargs = self._kwargs

        if kwargs:
            opKwargs.update(kwargs)
            rv = self
        
        if args:
            if len(args) == 1:
                func = args[0]
                assert callable(func)
                rv = self._decorationFunction(func, **opKwargs)
            else:
                raise NotImplementedError("Only one argument expected: taget callable. Got: {}".format(
                    args
                ))
        
        return rv

class BindingDescriptor(object):

    def __init__(self, constructor):
        super(BindingDescriptor, self).__init__()
        assert callable(constructor)
        self.constructor = constructor
        self.__name__ = constructor.__name__

    def __get__(self, objSelf, type=None):
        return self.getBoundObject(objSelf)

    def getBoundObject(self, bindingTarget):
        func = self.constructor
        name = "_refreshed_cache_for_{!r}_0x{:X}".format(func.__name__, id(func))
        try:
            return getattr(bindingTarget, name)
        except AttributeError:
            handle = func(bindingTarget)
            setattr(bindingTarget, name, handle)
            return handle

def parametricDecorator(payload):
    """This is decorator function that makes another function a
    configurable (via kwargs) decorator function.
    """
    return ParametricDecorator(payload)