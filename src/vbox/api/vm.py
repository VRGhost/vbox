import datetime
import itertools
import re
import time

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

class State(base.SubEntity):

    vm = None
    cli = property(lambda s: s.vm.cli)

    pause = lambda s: s.source.pause()
    resume = lambda s: s.source.resume()
    reset = lambda s: s.source.reset()
    powerOff = lambda s: s.source.poweroff()
    start = lambda s, **kw: s.source.start(**kw)

    # Mutable state is when hardware parameters of VM can be changed.
    mutable = property(lambda s: s.val in ("poweroff", "aborted"))

    knownStates = (
        "running", "paused", "poweroff",
        "aborted", "stopping", "saved",
    )

    @props.SourceProperty
    def val(self):
        rv = self.source.info.get("VMState")
        assert rv in self.knownStates, repr(rv)
        return rv

    for name in knownStates:
        locals()[name] = (lambda X: property(lambda s: s.val == X))(name)
    del name

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

    changeTime = props.SourceProperty(lambda s: datetime.datetime.strptime(
        s.source.info.get("VMStateChangeTime")[:-3], "%Y-%m-%dT%H:%M:%S.%f"))

    storageControllers = state = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.storageControllers = storageController.Library(self)
        self.state = State(self)

    def destroy(self):
        self.registered = True
        self.source.destroy()

    @props.SourceProperty
    def bootOrder(self):
        data = {}
        nameRe = re.compile("^boot(\d+)$")
        for (name, value) in self.source.info.iteritems():
            match = nameRe.match(name)
            if match:
                data[int(match.group(1))] = value

        keys = sorted(data.keys())
        ordered = [data[key] for key in keys]

        out = []
        for el in ordered:
            if el == "none":
                value = None
            else:
                value = el
            out.append(value)
        return tuple(out)

    @bootOrder.setter
    def bootOrder(self, new):
        old = self.bootOrder
        if len(new) > len(old):
            raise ValueError("Expecting no greater than {} elements.".format(new))

        callKw = {}
        for (idx, (prev, new)) in enumerate(
            itertools.izip_longest(old, new, fillvalue=None),
            start=1,
        ):
            if prev != new:
                # Apply the change
                if new is None:
                    value = "none"
                else:
                    value = new
                callKw["boot{}".format(idx)] = value
        
        if callKw:
            self.source.modify(**callKw)


    def wait(self, timeout=None):
        """Wait for VM to exit running state."""
        if timeout:
            endTime = time.time() + timeout
            timeOk = lambda: time.time() < endTime
        else:
            timeOk = lambda: True

        while (not self.state.mutable) and timeOk():
            time.sleep(0.2)
            self.source.clearCache()

        return self.state.mutable

class Library(base.Library):

    entityCls = VM

    def new(self, name):
        """Create new virtual machine with name `name`."""
        src = self.source.new(name)
        if not self.source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src, self)