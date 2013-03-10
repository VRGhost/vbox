
from . import chgCmds, infoCmds, base
from .list import List

class VBoxManage(base.Command):
    """Python representation of VboxManage executable."""

    def __init__(self, vb, executable="VBoxManage"):
        super(VBoxManage, self).__init__(vb, executable)

        self.list = List(self)
        self.showhdinfo = infoCmds.ShowHdInfo(self)
        self.showvminfo = infoCmds.ShowVmInfo(self)

        self.createhd = chgCmds.CreateHD(self)
        self.createvm = chgCmds.CreateVM(self)
        self.unregistervm = chgCmds.UnregisterVM(self)
        self.storagectl = chgCmds.StorageCtl(self)
        self.storageattach = chgCmds.StorageAttach(self)

        self.startvm = chgCmds.StartVm(self)
        self.controlvm = chgCmds.ControlVm(self)