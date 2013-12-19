from . import (
    base,
    network,
    ports,
    shared,
    storage,
    usb,
)

class VM(base.ConfigEntity):

    setAttrs = (
        "acpi", "cpuCount", "cpuExecutionCap",
        "memory", "videoMemory",
        "accelerate3d", "videoMemory",
        "groups", "biosTimeInUtc",
    )

    ignoreKeys = ("name", )
    customHandlers = ("osType", )

    subConfigs = {
        "media": storage.Controller,
        "network": network.Network,
        "serial": ports.Serial,
        "shared": shared.Shared,
        "usb": usb.Usb,
    }

    def fromDict(self, data, force=False):
        vmObj = self.api.vms.get(data["name"])
        if vmObj and (not force):
            self.ensure(vmObj, data)
        else:
            if not vmObj:
                vmObj = self.api.vms.create(data["name"])
            self.setup(vmObj, data)
        return vmObj

    def ensure_osType(self, vm, value):
        if value not in (vm.osType.description, vm.osType.id):
            raise self.exceptions.EnsureMismatch(vm, "osType", vm.osTypeNames(), value)

    def setup_osType(self, vm, value):
        vm.osType = value

class VirtualBox(object):

    def __init__(self, api):
        super(VirtualBox, self).__init__()
        self.api = api
        self.VM = VM(self)