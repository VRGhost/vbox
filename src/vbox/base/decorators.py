class ParametricDecorator(object):

    def __init__(self, target):
        super(ParametricDecorator, self).__init__()
        assert callable(target)
        self._decorationFunction = target
        self._kwargs = {}

    def __call__(self, *args, **kwargs):
        if kwargs:
        elif args:
        else:
            raise NotImplementedError(args, kwargs)

def parametricDecorator(func):
    """This is decorator function that makes another function a
    configurable (via kwargs) decorator function.
    """
    return ParametricDecorator(func)