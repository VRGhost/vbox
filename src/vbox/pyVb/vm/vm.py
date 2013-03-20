"""VM class."""
import re
import time
import datetime
from collections import defaultdict, OrderedDict

from vbox.cli import CmdError

from .. import util as props

from . import base, util
from .storageController import ControllerGroup
from .nic import NicGroup
from .state import State

class VM(base.VirtualBoxEntity):
    
    _blockTimeout = 15
    _attemptCount = 5

    vm = property(lambda self: self)
    cli = property(lambda s: s.vb.cli)

    baloon = props.Int(
        "guestmemoryballoon", extraCb=util.controlCb("guestmemoryballoon"))
    cpuCount = props.Int("cpus")
    cpuExecutionCap = props.Int("cpuexecutioncap")
    memory = props.Int("memory")
    videoMemory = props.Int("vram")

    cpuHotplug = props.Switch("cpuhotplug")
    acpi = props.Switch("acpi")
    ioapic = props.Switch("ioapic")
    pae = props.Switch("pae")
    accelerate3d = props.Switch("accelerate3d")

    enableHwVirt = props.Switch("hwvirtex")
    nestedPaging = props.Switch("nestedpaging")

    registered = property(lambda s: s in s.vb.vms.list())

    name = property(lambda s: s.getProp("name"))
    idProps = ("name", "UUID", "_initId")
    ostype = property(lambda s: s.vb.info.ostypes.find(s.getProp("ostype")).id)
    changeTime = property(lambda s: datetime.datetime.strptime(
        s.getProp("VMStateChangeTime")[:-3], "%Y-%m-%dT%H:%M:%S.%f"))

    controllers = state = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.state = State(self)
        self.controllers = ControllerGroup(self)
        self.nics = NicGroup(self)
        self.cli.addPostCmdExecListener(self._onExecCmd)

    def destroy(self, complete=True):
        if self.state.running:
            self.state.powerOff()

        self.cli.manage.unregistervm(self.getId(), delete=complete)
        super(VM, self).destroy()

    def unregister(self, delete=True):
        return self.destroy(complete=delete)

    def start(self, headless=True, blocking=True):
        if self.state.running:
            return

        if headless:
            startvm = lambda: self.cli.manage.startvm(self.name, type="headless")
        else:
            startvm = lambda: self.cli.manage.startvm(self.name)

        errMem = None

        for _att in self._loopySleep(lambda: self.state.running):
            if errMem:
                # Re-raise error from previous iteration
                raise errMem

            try:
                out = startvm()
            except CmdError as err:
                # Sometimes starvm() may return non-zero code with VM actually being sucesfully started
                out = errMem = err
            else:
                errMem = None

        if self.state.running:
            # virtual machine is still running
            return True
        else:
            raise Exception("Failed to start VM.\n.{}".format(out))

    def wait(self, timeout=None):
        """Wait for VM to exit running state."""
        if timeout:
            endTime = time.time() + timeout
            timeOk = lambda: time.time() < endTime
        else:
            timeOk = lambda: True

        while self.state.running and timeOk():
            time.sleep(0.1)

        return (not self.state.running)

    def powerOff(self, blocking=True):
        if not self.state.running:
            return

        self.cli.manage.controlvm.poweroff(self.name)

        if blocking:
            for _att in self._loopySleep(lambda: not self.state.running):
                self.updateInfo(True)
        # virtualbox sometimes is not fast enough to terminate VM process
        # so do a bit of waiting anyway.
        time.sleep(0.5)

    def _loopySleep(self, checkCb, attempts=None, timeout=None):
        if not attempts:
            attempts = self._attemptCount

        if not timeout:
            timeout = self._blockTimeout

        refreshFreq = 10
        completed = False

        for _att in xrange(attempts):
            time.sleep(_att * 2)
            # Yield to caller to do his stuff
            yield

            for _block in xrange(timeout * refreshFreq):
                if checkCb():
                    completed = True
                    break
                time.sleep(1.0 / refreshFreq)

            if completed:
                break

    @property
    def ide(self):
        typ = "ide"
        name = "Default {!r} Controller".format(typ)
        obj = self.controllers.get(type=typ, name=name)
        if not obj:
            obj = self.controllers.create(name=name, type=typ)
        return obj

    @property
    def sata(self):
        typ = "sata"
        name = "Default {!r} Controller".format(typ)
        obj = self.controllers.get(type=typ, name=name)
        if not obj:
            obj = self.controllers.create(name=name, type=typ)
        return obj

    @property
    def floppy(self):
        typ = "floppy"
        name = "Default {!r} Controller".format(typ)
        obj = self.controllers.get(type=typ, name=name)
        if not obj:
            obj = self.controllers.create(name=name, type=typ)
        return obj

    def clone(self, **kwargs):
        if kwargs.get("register") is None:
            kwargs["register"] = self.registered
        if "name" in kwargs:
            kwargs["name"] = kwargs["name"].format(parent=self)
        return self.vb.vms.clone(self.getId(), **kwargs)

    def onInfoUpdate(self):
        super(VM, self).onInfoUpdate()
        self.controllers.updateInfo(True)
        self.nics.updateInfo(True)

    def _getInfo(self):
        txt = self.cli.manage.showvminfo(self._initId)
        if txt:
            return OrderedDict(self.cli.util.parseMachineReadableFmt(txt))
        else:
            return None

    def setProp(self, name, value):
        self.modify({name: value})

    def modify(self, props, quiet=False):
        if self.state.running:
            if quiet:
                return False
            else:
                raise Exception("VM in running. Can not {}".format(props))
        modifyVmCmd = []
        for (name, value) in props.iteritems():
            modifyVmCmd.extend(("--" + name, value))

        self.cli.manage.modifyvm(self.id, *modifyVmCmd)

    def control(self, props, quiet=False):
        if not self.state.running:
            # Controlvm is only meaningful when VM is running
            if quiet:
                return False
            else:
                raise Exception("VM in not running. Can not {}".format(props))

        self.cli.manage.controlvm(**props)


    def _onExecCmd(self, source, cmd, rc):
        if source.changesVmState:
            doExec = False
            for myId in self.iterIds():
                if str(myId) in cmd:
                    doExec = True
                    break
            if doExec:
                self.updateInfo(True)