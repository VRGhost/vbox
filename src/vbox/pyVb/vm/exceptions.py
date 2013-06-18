class VmInaccessible(Exception):

    def __init__(self, vmId):
        super(VmInaccessible, self).__init__("Can not access VM {!r}".format(vmId))
        self.vmId = vmId