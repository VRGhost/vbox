"""Commands that alter virtualbox states.

Virtual machine-related commands

"""

from .. import (
    base,
    util,
)

class VMInfoParser(util.parsers.Dict):

    sep = '='

class ShowVMInfo(base.SubCommand):

    formatter = util.Formatter(
        all=("target", ),
        mandatory=("target", ),
        positional=("--details", "--machinereadable", "{target}", ),
    )
    # outCheck = util.OutCheck(okRc=(0, 1))
    parser = VMInfoParser()

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
        positional=("{source}", ),
        flags=("register", )
    )

class UnregisterVM(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "delete"),
        mandatory=("target", ),
        flags=("delete", ),
        positional=("{target}", ),
    )

class RegisterVM(base.SubCommand):

    formatter = util.Formatter(
        all=("target",),
        mandatory=("target", ),
        positional=("{target}", ),
    )

class StartVM(base.SubCommand):
    """Start VM."""

    formatter = util.Formatter(
        all=("target", "type"),
        positional=("{target}",),
        mandatory=("target", )
    )

class ControlVM(base.SubCommand):


    def _toCmdLine(self, args, kwargs):
        """ControlVm is actually more like a sub-command with more sub-commands.

        I want to make a shortcut here and omit creating these sub-sub commands.

        Instead, this object will declare methods that provide necessary interface and
        its __call__ method will not expect any kwargs at all. It will simply forward "args" as mapped argument string.
        """
        assert not kwargs
        rv = ["controlvm"]
        rv.extend(args)
        return tuple(rv)

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

class ModifyVmFormatter(util.Formatter):
    """Modify VM has too many fields for me to bother defining them.

    Instead, the formatter accepts one mandatory argument "target" and
    maps rest kwargs to the named params directly.
    """

    multiArgKeys = (
        # List of keys that are followed by the multiple separate command line arguments
        # The list to pass is represended by the list of values passed in the dictionary.
        "uart1",
        "uart2",
        "uartmode1",
        "uartmode2",
    )

    def verify(self, data):
        "There is only one strict requirement -- 'target' must be present."
        if not data.has_key("target"):
            raise TypeError("'target' not provided.")

    def castValues(self, data):
        preserved = {}
        for name in self.multiArgKeys:
            try:
                preserved[name] = data[name]
            except KeyError:
                pass
        rv = super(ModifyVmFormatter, self).castValues(data)
        rv.update(preserved)
        return rv



class ModifyVM(base.SubCommand):
    """ModifyVm bindings."""

    formatter = ModifyVmFormatter(
        all=("target", ),
        mandatory=("target", ),
        positional=("{target}", ),
    )