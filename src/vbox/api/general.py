from collections import defaultdict

from . import base

sep = '/'

def groupsToCli(vals):
    def _mkGroup(inp):
        if isinstance(inp, basestring):
            path = inp
        else:
            path = sep.join(str(el) for el in inp)
        if not path.startswith(sep):
            path = sep + path
        return path
    if not vals:
        vals = ("", )
    return (_mkGroup(el) for el in vals)

class DetachedGeneral(base.Base):

    kwargName = "general"
    expectedKwargs = {
        "name": 1,
        "osType": 1,
        "directory": (0, 1),
        "groups": lambda cnt: True,
    }
    defaultKwargs = {
        "directory": None,
        "groups": None,
    }

class InteractiveGeneral(base.Child):

    kwargName = DetachedGeneral.kwargName
    expectedKwargs = DetachedGeneral.expectedKwargs
    defaultKwargs = defaultdict(lambda: None)

    osType = base.pyVmProp("osType")
    directory = base.pyVmProp("rootDir")

    def __init__(self, detached):
        super(InteractiveGeneral, self).__init__(
            **detached.boundKwargs)

    def groups():
        doc = "The groups property."
        def fget(self):
            def _parseGroup(el):
                path = el.split(sep)
                assert not path[0]
                path.pop(0)
                return tuple(el for el in path if el)
            rv = (_parseGroup(el) for el in self.pyVm.groups)
            return tuple(el for el in rv if el)
        def fset(self, value):
            self.pyVm.groups = groupsToCli(value)
        return locals()
    groups = property(**groups())

    def befoureSetup(self, kwargs):
        # Remove 'directory' if it was defined.
        # It is not possible to change that is VM had been already created.
        # And by the time `InteractiveGeneral` is initalised,
        # VM should already exist
        kwargs.pop("directory", None)