"""Commands that alter virtualbox states."""

from .subCmd import (
    CmdError,
    Generic,
    PlainCall,
    VmCmd,
    VmPropSetter,
)

from . import util


class CreateHD(Generic):

    changesVmState = True
    opts = ("filename", "size", "format", "variant")
    mandatory = ("filename", "size")

    def getRcHandlers(self):
        return {
            0: self._findErrors,
        }

    def _findErrors(self, cmd, output):
        txt = output.lower()
        if ("error:" in txt) or ("verr_" in txt):
            raise CmdError(cmd, 0, output)
        elif not txt:
            raise Exception("Expected for `createhd` to write something to the output.")
        return output

class CreateVM(Generic):

    changesVmState = True
    opts = ("name", "groups", "ostype", "basefolder", "uuid")
    flags = ("register", )
    mandatory = ("name", )


class UnregisterVM(VmCmd):

    changesVmState = True
    flags = ("delete", )

class StorageCtl(VmPropSetter):

    changesVmState = True
    propName = "--name"
    opts = ("add", "controller", "sataportcount")
    bools = ("hostiocache", "bootable")
    flags = ("remove")

class StorageAttach(VmPropSetter):

    changesVmState = True
    propName = "--storagectl"
    opts = ("port", "device", "type", "medium",)
    mandatory = ("type", )


class StartVm(VmCmd):
    """Start VM."""

    changesVmState = True
    opts = ("type", )

class ControlVm(VmPropSetter):

    changesVmState = True
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

class ModifyVm(PlainCall):
    """ModifyVm bindings."""

    changesVmState = True
    # This function has vay too many parameters to
    # bother declaring them here.
    # Plus, it is the one that is most likely to change
    # (Judging number of parameters again.) 
    # 
    # This is why it had been declared PlainCall and
    # one has to pass parameters in array rather nice
    # kwargs.
    #
    # No validation is performed.