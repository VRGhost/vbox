from .. import base
from . import (
    commands,
    manage_list,
)

class VBoxManage(base.RealCommand):
    """Python representation of VboxManage executable."""

    fields = None
    
    def __init__(self, parent, executable="VBoxManage"):
        super(VBoxManage, self).__init__(parent, executable)

        self.fields = fields = {}
        for cls in (
            commands.ShowHdInfo,
            commands.CreateHD,
            manage_list.List,
        ):
            obj = cls(self.interface, self)
            name = cls.__name__
            name = name[0].lower() + name[1:]

            setattr(self, name, obj)
            fields[name] = obj