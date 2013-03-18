from . import base

class VM(base.Base):

    expectedKwargs = {
        "general": 1,
        "system": 1,
        "display": 1,
        "storage": 1,
    }