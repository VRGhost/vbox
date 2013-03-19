from . import base

class General(base.Base):

    kwargName = "general"
    expectedKwargs = {
        "name": 1,
        "osType": 1,
    }