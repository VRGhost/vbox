"""Utility functions."""

def mutating(fn):
    def __wrapper__(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        finally:
            self.refresh()
    return __wrapper__

def controlCb(name):
    def __callback__(self, value):
        self.control({name: value}, quiet=True)
    return __callback__