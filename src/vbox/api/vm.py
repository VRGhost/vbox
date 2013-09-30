import datetime
import itertools
import os
import re
import time

from . import (
    base,
    guest,
    meta,
    network,
    props,
    storageController,
)

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
        None, # VirtualBox was not ready to provide valid vm info.
        "running", "paused", "poweroff",
        "aborted", "stopping", "saved",
    )

    @props.SourceProperty
    def val(self):
        rv = self.source.info.get("VMState")
        assert rv in self.knownStates, repr(rv)
        return rv

    for name in knownStates:
        if name:
            locals()["is{}".format(name.title())] = (lambda X: (lambda s: s.val == X))(name)
    del name

class VM(base.Entity):
    """Virtual machine entity."""

    UUID = props.Str(lambda s: s.source.info.get("UUID"))
    name = props.Str(lambda s: s.source.info.get("name"))

    acpi = props.OnOff(**props.modify("acpi"))
    cpuCount = props.Int(**props.modify("cpus"))
    cpuExecutionCap = props.Int(**props.modify("cpuexecutioncap"))
    memory = props.Int(**props.modify("memory"))
    videoMemory = props.Int(**props.modify("vram"))
    osType = props.Str(**props.modify("ostype"))

    destroy = lambda s: s._source.destroy()
    registered = props.SourceProperty(
        fget=lambda s: s.library.isRegistered(s),
        fset=lambda s, v: s.source.register() if v else s.source.unregister(),
        getDepends=lambda s: (s, s.library),
    )

    changeTime = props.SourceProperty(lambda s: datetime.datetime.strptime(
        s.source.info.get("VMStateChangeTime")[:-3], "%Y-%m-%dT%H:%M:%S.%f"))

    storageControllers = state = meta = storage = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)

        self.storageControllers = storageController.Library(self)
        self.storage = storageController.DriveAccessor(self.storageControllers)
        self.state = State(self)
        self.meta = meta.Meta(self.source.extraData)
        self.guest = guest.GuestAdditions(self.source)

    def destroy(self):
        self.registered = True
        self.source.destroy()

    @props.SourceProperty
    def nics(self):
        nameRe = re.compile("^nic(\d+)$")
        out = []
        for name in self.source.info.iterkeys():
            match = nameRe.match(name)
            if match:
                out.append(network.BoundNIC(self, int(match.group(1))))

        out.sort(key=lambda nic: nic.idx)
        return tuple(out)

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

    def _onSourceException(self, exc):
        if isinstance(exc, self.source.exceptions.VmNotFound):
            raise self.exceptions.VmNotFound()

    def groups():
        def fget(self):
            strVal = self.source.info.get("groups")
            if not strVal:
                return ()
            return tuple(strVal.split(","))
        def fset(self, value):
            out = []
            for el in value:
                if not el.startswith("/"):
                    el = "/" + el
                out.append(el)
            if not out:
                out.append("/")

            self.source.modify(groups=",".join(out))
        return locals()
    groups = props.SourceProperty(**groups())

    def clone(self, name=None, autoname=False, baseDir=None, register=True):
        """Clone virtual machine.

        http://www.virtualbox.org/manual/ch08.html#vboxmanage-clonevm

        Parameters:
            - `name` - name for the new vm to be cloned;
            - `basedir` - path where clone will be stored;
            - `register` (default: `True`) - if the new vm has to be registered at the virtualbox;

            returns new api.VM instance
        """
        if not baseDir:
            baseDir = self.interface.host.defaultVmDir
        if not os.path.isdir(baseDir):
            raise self.exceptions.ApiError("Base directory {!r} is not acessible".format(baseDir))

        def _nameGen(name, autoname):
            if name and (not autoname):
                yield name
            else:
                name = name or self.name
                yield name
                for idx in itertools.count(2):
                    yield "{} ({})".format(name, idx)

        for testName in _nameGen(name, autoname):
            if (not os.path.exists(os.path.join(baseDir, testName))) and \
                self.library.get(testName) is None \
            :
                break
        else:
            raise self.exceptions.ApiError("Unable to generate unique VM name for {!r}".format(name))

        self.source.clone(testName, baseDir, register)
        rv = self.library.get(testName)
        assert rv is not None
        return rv

class Library(base.Library):

    entityCls = VM

    def get(self, name):
        srcObj = self.source.new(name)
        if srcObj.exists():
            rv = self.entityCls(srcObj, self)
        else:
            rv = None
        return rv

    def create(self, name):
        srcObj = self.source.new(name)
        if srcObj.exists():
            raise self.exceptions.VmAlreadyExists(name)
        else:
            srcObj.create(register=True)
            rv = self.entityCls(srcObj, self)
        return rv

    def getOrCreate(self, name):
        """Create new virtual machine with name `name`."""
        src = self.source.new(name)
        if not self.source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src, self)