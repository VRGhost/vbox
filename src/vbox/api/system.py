from . import base

class System(base.Child):

    kwargName = "system"
    expectedKwargs = {
        "memory": (0, 1),
    }

    defaultKwargs = {
        "memory": None,
    }

    def memory():
        doc = "The memory property."
        def fget(self):
            return self.pyVm.memory
        def fset(self, value):
            self.pyVm.memory = value
        return locals()
    memory = property(**memory())