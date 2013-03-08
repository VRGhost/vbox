"""Commands that alter virtualbox states."""

from .subCmd import Generic, PlainCall, VmPropSetter

from . import util

class CreateHD(Generic):

    longOpts = ("filename", "size", "format", "variant")
    mandatory = ("filename", "size")

    def getRcHandlers(self):
        return {
            0: self._findErrors,
        }

    def _findErrors(self, output):
        txt = output.lower()
        if ("error:" in txt) or ("verr_" in txt):
            raise Exception("Failed to create HDD:\n====\n{}\n====\n".format(output))
        elif not txt:
            raise Exception("Expected for `createhd` to write something to the output.")
        return True

class CreateVM(Generic):

    longOpts = ("name", "groups", "ostype", "register", "basefolder", "uuid")
    mandatory = ("name", )
    boolOpts = ("register", )

    def getRcHandlers(self):
        return {
            0: self._parse,
        }

    def _parse(self, txt):
        return util.parseParams(txt)


class UnregisterVM(PlainCall):

    def __call__(self, name, delete=False):
        cmd = [name]
        if delete:
            cmd.append("--delete")
        return self.checkOutput(cmd)


class StorageCtl(PlainCall):

    
    def __call__(self, vmName, name, add=None, controller=None, sataportcount=None, hostiocache=None, bootable=None, remove=None):
        cmd = [vmName, "--name", name]
        if add:
            cmd.extend(("--add", add))
        if controller:
            cmd.extend(("--controller", controller))
        if sataportcount:
            cmd.extend(("--sataportcount", int(sataportcount)))
        if hostiocache is not None:
            cmd.extend(("--hostiocache", "on" if hostiocache else "off"))
        if bootable is not None:
            cmd.extend(("--bootable", "on" if bootable else "off"))
        if remove:
            cmd.append("--remove")
        return self.checkOutput(cmd)


class StorageAttach(VmPropSetter):

    longOpts = ("storagectl", "port", "device", "type", "medium",)
    mandatory = ("storagectl", )

