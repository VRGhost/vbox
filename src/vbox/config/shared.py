import os

from . import base

class Shared(base.SubConfigEntity):

    customHandlers = ("targets", )

    def setup_targets(self, vm, data):
        for folderCfg in data:
            vm.shared.set(folderCfg["name"], folderCfg["path"])

    def ensure_targets(self, vm, data):
        for folderCfg in data:
            name = folderCfg["name"]
            try:
                path = vm.shared.get(name).path
            except KeyError:
                raise self.exceptions.ConfigMismatch("No shared folder {!r}".format(name))
            if os.path.abspath(path) != os.path.abspath(folderCfg["path"]):
                raise self.exceptions.ConfigMismatch("VM folder {!r} should be pointing to {!r}, instead it points to {!r}".format(
                    name, data["path"], path
                ))