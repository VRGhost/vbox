from . import base

class Display(base.Child):

    kwargName = "display"
    expectedKwargs = {
        "accelerate3d": (0, 1),
        "memory": (0, 1),
    }

    defaultKwargs = {
        "accelerate3d": None,
        "memory": None,
    }

    accelerate3d = base.pyVmProp("accelerate3d")
    memory = base.pyVmProp("videoMemory")