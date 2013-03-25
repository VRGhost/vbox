
from . import chgCmds, infoCmds, extraData, base
from .list import List

class VBoxManage(base.CliVirtualBoxElement):
    """Python representation of VboxManage executable."""

    _cliAccessor = None
    
    def __init__(self, parent, executable="VBoxManage"):
        super(VBoxManage, self).__init__(parent)
        self._cliAccessor = _cli = base.Command(self, executable)

        _parts = {
            "controlvm": chgCmds.ControlVm(_cli),
            "createhd": chgCmds.CreateHD(_cli),
            "createvm": chgCmds.CreateVM(_cli),
            "list": List(_cli),
            "showhdinfo": infoCmds.ShowHdInfo(_cli),
            "showvminfo": infoCmds.ShowVmInfo(_cli),
            "startvm": chgCmds.StartVm(_cli),
            "storageattach": chgCmds.StorageAttach(_cli),
            "storagectl": chgCmds.StorageCtl(_cli),
            "unregistervm": chgCmds.UnregisterVM(_cli),
            "modifyvm": chgCmds.ModifyVm(_cli),
            "clonevm": chgCmds.CloneVM(_cli),
            "clonehd": chgCmds.CloneHd(_cli),
            "getextradata": extraData.GetExtraData(_cli),
            "setextradata": extraData.SetExtraData(_cli),
        }

        for (name, obj) in _parts.iteritems():
            setattr(self, name, obj)

        self._executables = tuple(_parts.values())

    def addPreCmdExecListener(self, cb):
        _cancellers = [el.addPreCmdExecListener(cb)
            for el in self._executables]
        return lambda: [fn() for fn in _cancellers]

    def addPostCmdExecListener(self, cb):
        _cancellers = [el.addPostCmdExecListener(cb)
            for el in self._executables]
        return lambda: [fn() for fn in _cancellers]