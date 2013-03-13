"""VM class."""
import re
import time
import datetime
from collections import defaultdict, OrderedDict

from . import base, util
from . import vmProps as props
from ..cli import util, CmdError
from .storageController import ControllerGroup
from .nic import NicGroup

class VM(base.VirtualBoxEntity):
    
    _blockTimeout = 15
    _attemptCount = 5

    vm = property(lambda self: self)
    cli = property(lambda s: s.vb.cli)

    memory = props.Int("memory")

    name = property(lambda s: s.getProp("name"))
    idProps = ("name", "UUID", "_initId")
    state = property(lambda s: s.getProp("VMState"))
    ostype = property(lambda s: s.vb.info.ostypes.find(s.getProp("ostype")).id)
    changeTime = property(lambda s: datetime.datetime.strptime(
        s.getProp("VMStateChangeTime")[:-3], "%Y-%m-%dT%H:%M:%S.%f"))

    running = property(lambda s: s.state == "running")
    paused = property(lambda s: s.state == "paused")

    pause = lambda s: s.cli.manage.controlvm.pause(s.name)
    resume = lambda s: s.cli.manage.controlvm.resume(s.name)
    reset = lambda s: s.cli.manage.controlvm.reset(s.name)
    powerOff = lambda s: s.cli.manage.controlvm.poweroff(s.name)

    controllers = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.controllers = ControllerGroup(self)
        self.nics = NicGroup(self)
        self.cli.addPostCmdExecListener(self._onExecCmd)

    def destroy(self, complete=True):
        self.cli.manage.unregistervm(self.getId(), delete=complete)
        super(VM, self).destroy()

    def unregister(self, delete=True):
        return self.destroy(complete=delete)

    def start(self, headless=True, blocking=True):
        if self.running:
            return

        if headless:
            startvm = lambda: self.cli.manage.startvm(self.name, type="headless")
        else:
            startvm = lambda: self.cli.manage.startvm(self.name)

        refreshFreq = 10
        for _att in xrange(self._attemptCount):
            time.sleep(_att * 2)
            try:
                startvm()
            except CmdError as err:
                # Sometimes starvm() may return non-zero code with VM actually being sucesfully started
                errMem = err
            else:
                errMem = None

            for _block in xrange(self._blockTimeout * refreshFreq):
                if self.running:
                    break
                time.sleep(1.0 / refreshFreq)

            if self.running:
                break

            if errMem:
                # We hadn't broken out of the loop previously
                raise errMem

        if self.running:
            # virtual machine is still running
            return True
        else:
            raise Exception("Vm process stopped with return code {}.".format(proc.poll()))

    def wait(self, timeout=None):
        """Wait for VM to exit running state."""
        if timeout:
            endTime = time.time() + timeout
            timeOk = lambda: time.time() < endTime
        else:
            timeOk = lambda: True

        while self.running and timeOk():
            time.sleep(0.1)

        return (not self.running)

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

    def onInfoUpdate(self):
        super(VM, self).onInfoUpdate()
        self.controllers.updateInfo(True)

    def _getInfo(self):
        txt = self.cli.manage.showvminfo(self._initId)
        if txt:
            return OrderedDict(util.parseMachineReadableFmt(txt))
        else:
            return None

    def setProp(self, name, value):
        self.modify({name: value})

    def modify(self, props):
        cmd = []
        for (name, value) in props.iteritems():
            cmd.extend(("--" + name, value))
        self.cli.manage.modifyvm(self.id, *cmd)

    def _onExecCmd(self, source, cmd, rc):
        if source.changesVmState:
            doExec = False
            for myId in self.iterIds():
                if str(myId) in cmd:
                    doExec = True
                    break
            if doExec:
                self.updateInfo(True)