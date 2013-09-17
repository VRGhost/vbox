"""Commands that alter virtualbox states."""

from .. import (
    base,
    util,
)

class ShowHdInfo(base.SubCommand):

    formatter = util.Formatter(
        all=("target", ),
        mandatory=("target", ),
        positional=("target", ),
    )
    outCheck = util.OutCheck(okRc=(0, 1))

class ShowVmInfo(base.SubCommand):

    formatter = util.Formatter(
        all=("target", ),
        mandatory=("target", ),
        positional=("--details", "--machinereadable", "{target}", ),
    )
    outCheck = util.OutCheck(okRc=(0, 1))

class CreateHD(base.SubCommand):

    formatter = util.Formatter(
        all=("filename", "size", "format", "variant"),
        mandatory=("filename", "size"),
        positional=("createhd", ),
    )
    outCheck = util.OutCheck(
        okRc=(0, ),
        extraChecks={
            0: lambda cmd, out: out and (not any(infix in out for infix in ("error:", "verr_"))),
        }
    )


class CreateVM(base.SubCommand):

    formatter = util.Formatter(
        all=("name", "groups", "ostype", "basefolder", "uuid", "register"),
        mandatory=("name", ),
        flags=("register", )
    )

class CloneVM(base.SubCommand):

    formatter = util.Formatter(
        all=("source", "snapshot", "mode", "options", "name", "basefolder", "uuid", "register"),
        mandatory=("source", ),
        flags=("register", )
    )

class CloneHd(base.SubCommand):

    formatter = util.Formatter(
        all=("source", "destanation", "format", "variant", "existing"),
        mandatory=("source", "destanation"),
        flags=("existing", ),
        positional=("source", "destanation"),
    )


class UnregisterVM(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "delete"),
        mandatory=("target", ),
        flags=("delete", ),
        positional=("target", ),
    )

class StorageCtl(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "name", "add", "controller", "sataportcount", "hostiocache", "bootable", "remove"),
        positional=("target", ),
        mandatory=("target", "name"),
        flags=("remove", ),
        onOff=("hostiocache", "bootable"),
    )

class StorageAttach(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "storagectl", "port", "device", "type", "medium"),
        mandatory=("target", "storagectl"),
        positional=("target", ),
    )


class StartVm(base.SubCommand):
    """Start VM."""

    formatter = util.Formatter(
        all=("target", "type"),
        positional=("target",),
        mandatory=("target", )
    )

class ControlVm(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "action"),
        positional=("target", "action"),
        mandatory=("target", "action"),
    )

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

# class ModifyVm(PlainCall):
#     """ModifyVm bindings."""

#     changesVmState = True
#     # This function has vay too many parameters to
#     # bother declaring them here.
#     # Plus, it is the one that is most likely to change
#     # (Judging number of parameters again.) 
#     # 
#     # This is why it had been declared PlainCall and
#     # one has to pass parameters in array rather nice
#     # kwargs.
#     #
#     # No validation is performed.