"""Commands that alter virtualbox states."""

from .subCmd import Generic, PlainCall, VmPropSetter, CmdError

from . import util


class CreateHD(Generic):

    longOpts = ("filename", "size", "format", "variant")
    mandatory = ("filename", "size")

    def getRcHandlers(self):
        return {
            0: self._findErrors,
        }

    def _findErrors(self, cmd, output):
        txt = output.lower()
        if ("error:" in txt) or ("verr_" in txt):
            raise CreateError(cmd, output)
        elif not txt:
            raise Exception("Expected for `createhd` to write something to the output.")
        return output

class CreateVM(Generic):

    longOpts = ("name", "groups", "ostype", "register", "basefolder", "uuid")
    mandatory = ("name", )
    boolOpts = ("register", )


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
    mandatory = ("storagectl", "type")


class StartVm(VmPropSetter):
    """Start VM."""

    longOpts = ("type", )

class ControlVm(VmPropSetter):

    def __call__(self, name, action):
        return self.checkOutput([name, action])

    def pause(self, name):
        return self(name, "pause")

    def resume(self, name):
        return self(name, "resume")

    def reset(self, name):
        return self(name, "reset")

    def poweroff(self, name):
        return self(name, "poweroff")

    def savestate(self, name):
        return self(name, "savestate")