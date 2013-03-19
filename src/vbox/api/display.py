from . import base

class Display(base.Child):

    kwargName = "display"
    expectedKwargs = {
        "accelerate3d": (0, 1),
    }

    defaultKwargs = {
        "accelerate3d": None,
    }