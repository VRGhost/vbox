"""VM class."""
from collections import defaultdict, OrderedDict
import datetime
import os
import re
import time

from vbox.cli import CmdError

from .. import util as props

from . import (
    base,
    exceptions,
    util,
)
from .storageController import ControllerGroup
from .nic import NicGroup
from .state import State
from .extraData import ExtraData
from .guest import Guest

class VM(base.VirtualBoxEntity):
    
    _blockTimeout = 15
    _attemptCount = 5

    vm = property(lambda self: self)
    cli = property(lambda s: s.vb.cli)
    rootDir = property(lambda s: os.path.dirname(s.getProp("CfgFile")))

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

    groups = props.Tuple("groups", sep=',')

    name = property(lambda s: s.getProp("name"))
    idProps = ("name", "UUID", "_initId")
    changeTime = property(lambda s: datetime.datetime.strptime(
        s.getProp("VMStateChangeTime")[:-3], "%Y-%m-%dT%H:%M:%S.%f"))

    controllers = state = guest = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.state = State(self)
        self.controllers = ControllerGroup(self)
        self.nics = NicGroup(self)
        self.extraData = ExtraData(self)
        self.guest = Guest(self)

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

        while (not self.state.mutable) and timeOk():
            time.sleep(0.2)
            self.updateInfo(True)

        return self.state.mutable

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

    def suspend(self, blocking=True):
        if not self.state.running:
            return
        self.cli.manage.controlvm.savestate(self.name)

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
        """Only one IDE controller is allowed in the VirtualBox."""
        typ = "ide"
        obj = self.controllers.get(type=typ)
        if not obj:
            name = "Default {!r} Controller".format(typ)
            obj = self.controllers.create(name=name, type=typ)
        return obj

    @property
    def sata(self):
        typ = "sata"
        obj = self.controllers.get(type=typ)
        if not obj:
            name = "Default {!r} Controller".format(typ)
            obj = self.controllers.create(name=name, type=typ)
        return obj

    @property
    def floppy(self):
        typ = "floppy"
        obj = self.controllers.get(type=typ)
        if not obj:
            name = "Default {!r} Controller".format(typ)
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
        inaccessibleMark = "<inaccessible>"
        if self.info.get("name", inaccessibleMark) == inaccessibleMark:
            raise exceptions.VmInaccessible(self._initId)
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
                raise Exception("VM is running. Can not {}".format(props))
        modifyVmCmd = []
        for (name, value) in props.iteritems():
            modifyVmCmd.extend(("--" + name, value))

        if modifyVmCmd:
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

    def osType():
        doc = "The osType property."
        def fget(self):
            return self.vb.info.ostypes.find(
                self.getProp("ostype")).id
        def fset(self, value):
            newVal = self.vb.info.ostypes.find(value).id
            if newVal != self.osType:
                self.setProp("ostype", newVal)
        return locals()
    osType = property(**osType())