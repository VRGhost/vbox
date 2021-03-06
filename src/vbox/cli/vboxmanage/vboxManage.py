from .. import base
from . import (
    extraData,
    guest,
    hostNics,
    manage_list,
    storage,
    vm,
)

class VBoxManage(base.RealCommand):
    """Python representation of VboxManage executable."""

    fields = None

    def __init__(self, parent, executable="VBoxManage"):
        super(VBoxManage, self).__init__(parent, executable)

        self.fields = fields = {}
        for cls in (

            #VMs
            vm.CloneVM,
            vm.ControlVM,
            vm.CreateVM,
            vm.ModifyVM,
            vm.RegisterVM,
            vm.ShowVMInfo,
            vm.StartVM,
            vm.UnregisterVM,

            # Storage
            storage.CloneHd,
            storage.CloseMedium,
            storage.CreateHD,
            storage.ShowHdInfo,
            storage.StorageAttach,
            storage.StorageCtl,

            # List
            manage_list.List,

            # Extra data
            extraData.SetExtraData,
            extraData.GetExtraData,

            # Guest stuff
            guest.GuestProperty,
            guest.GuestControl,
            guest.SharedFolder,

            # Host network adapter management
            hostNics.HostOnlyIf,
        ):
            obj = cls(self.interface, self)
            name = cls.__name__
            name = name[0].lower() + name[1:]

            setattr(self, name, obj)
            fields[name] = obj