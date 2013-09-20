from . import (
    base,
    props,
    storageController,
)

def modify(name):
    return {
        "fget": lambda self: self.source.info.get(name),
        "fset": lambda self, value: self.source.modify(**{name: value}),
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
    registered = props.SourceProperty(
        fget=lambda s: s.library.isRegistered(s),
        fset=lambda s, v: s.source.register() if v else s.source.unregister(),
        getDepends=lambda s: (s, s.library),
    )

    storageControllers = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.storageControllers = storageController.Library(self)

    def destroy(self):
        self.registered = True
        self.source.destroy()

class Library(base.Library):

    entityCls = VM

    def new(self, name):
        """Create new virtual machine with name `name`."""
        src = self.source.new(name)
        if not self.source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src, self)