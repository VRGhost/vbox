from . import base, storage

class VM(base.ConfigEntity):

    setAttrs = (
        "acpi", "cpuCount", "cpuExecutionCap",
        "memory", "videoMemory",
        "osType", "accelerate3d", "videoMemory",
    )

    ignoreKeys = ("name", )

    subConfigs = {
        "media": storage.Controller,
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

class VirtualBox(object):

    def __init__(self, api):
        super(VirtualBox, self).__init__()
        self.api = api
        self.VM = VM(self)