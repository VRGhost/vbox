from . import base, props

def modify(name):
    return {
        "fget": lambda src: src.info.get(name),
        "fset": lambda self, value: self._source.modify(**{name: value}),
    }

class VM(base.Entity):
    """Virtual machine entity."""

    UUID = props.SourceStr(lambda src: src.info.get("UUID"))

    acpi = props.OnOff(**modify("acpi"))
    cpuCount = props.SourceInt("cpus")
    cpuExecutionCap = props.SourceInt("cpuexecutioncap")
    memory = props.SourceInt(**modify("memory"))
    videoMemory = props.SourceInt("vram")

    destroy = lambda s: s._source.destroy()

class Library(base.Library):

    entityCls = VM

    def new(self, name):
        """Create new virtual machine with name `name`."""
        src = self._source.new(name)
        if not self._source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src)