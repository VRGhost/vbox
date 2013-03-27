from . import base

class CPU(base.Child):

    kwargName = "cpu"
    expectedKwargs = {
        "count": (0, 1),
        "executionCap": (0, 1),
        "hotplug": (0, 1),
        "pae": (0, 1),
    }

    defaultKwargs = {}

    count = base.pyVmProp("cpuCount")
    executionCap = base.pyVmProp("cpuExecutionCap")
    hotplug = base.pyVmProp("cpuHotplug")
    pae = base.pyVmProp("pae")

class System(base.Child):

    kwargName = "system"
    expectedKwargs = {
        "cpu": (0, 1),
        "hwVirtualisation": (0, 1),
        "memory": (0, 1),
        "nestedPaging": (0, 1),
        "ioapic": (0, 1),
    }

    defaultKwargs = {
        "cpu": lambda s: CPU(),
    }

    hwVirtualisation = base.pyVmProp("enableHwVirt")
    ioapic = base.pyVmProp("ioapic")
    memory = base.pyVmProp("memory")
    nestedPaging = base.pyVmProp("nestedPaging")