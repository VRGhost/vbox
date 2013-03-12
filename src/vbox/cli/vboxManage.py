
from . import chgCmds, infoCmds, base
from .list import List

class VBoxManage(base.Command):
    """Python representation of VboxManage executable."""

    def __init__(self, vb, executable="VBoxManage"):
        super(VBoxManage, self).__init__(vb, executable)

        _parts = {
            "controlvm": chgCmds.ControlVm(self),
            "createhd": chgCmds.CreateHD(self),
            "createvm": chgCmds.CreateVM(self),
            "list": List(self),
            "showhdinfo": infoCmds.ShowHdInfo(self),
            "showvminfo": infoCmds.ShowVmInfo(self),
            "startvm": chgCmds.StartVm(self),
            "storageattach": chgCmds.StorageAttach(self),
            "storagectl": chgCmds.StorageCtl(self),
            "unregistervm": chgCmds.UnregisterVM(self),
            "modifyvm": chgCmds.ModifyVm(self),
        }

        for (name, obj) in _parts.iteritems():
            setattr(self, name, obj)

        self._executables = tuple(_parts.values())

    def addPreCmdExecListener(self, cb):
        _cancellers = [el.addPreCmdExecListener(cb)
            for el in self._executables]
        return lambda: [fn() for fn in _cancellers]