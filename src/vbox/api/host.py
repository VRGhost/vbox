import os
from . import base, props

class FuzzyPath(props.Str):

    def typeFrom(self, val):
        return val.replace('/', os.sep).replace('\\', os.sep)

class Host(base.Library):

    defaultVmDir = FuzzyPath(lambda s: s.source.properties["Default machine folder"])