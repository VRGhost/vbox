"""Utility functions."""

def mutating(fn):
    def __wrapper__(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        finally:
            self.refresh()
    return __wrapper__