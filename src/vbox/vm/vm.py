"""VM class."""
import re
import time
from collections import defaultdict, OrderedDict

from . import base, util
from ..cli import util, CmdError

class VM(base.RefreshableEntity):
    
    _blockTimeout = 15
    _attemptCount = 5

    name = property(lambda s: s.getProp("name"))
    idProps = base.VirtualBoxEntity.idProps + ("name", )
    state = property(lambda s: s.getProp("VMState"))
    running = property(lambda s: s.state == "running")
    paused = property(lambda s: s.state == "paused")

    pause = lambda s: s.cli.manage.controlvm.pause(s.name)
    resume = lambda s: s.cli.manage.controlvm.resume(s.name)
    reset = lambda s: s.cli.manage.controlvm.reset(s.name)
    powerOff = lambda s: s.cli.manage.controlvm.poweroff(s.name)

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self._controllers = []

    def destroy(self, complete=True):
        self.cli.manage.unregistervm(name=self.getId(), delete=complete)
        super(VM, self).destroy()

    def unregister(self, delete=True):
        return self.destroy(complete=delete)


    def findControllers(self, type):
        return (el for el in self._controllers if el.type == type)

    def getControoler(self, name):
        # Touch 'info' property to ensure that controller registy is up to date
        self.info
        for el in self._controllers:
            if el.name == name:
                return el

    def createController(self, name, type, **kwargs):
        assert not self.getControoler(name)
        self.cli.manage.storagectl(self.UUID, name, add=type)
        del self.info
        obj = self.getControoler(name)
        assert obj.type == type
        return obj

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
                self.refresh()
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
            for el in self.info.iteritems():
                print el
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
            self.refresh()

        return (not self.running)

    @property
    def ide(self):
        typ = "ide"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    @property
    def sata(self):
        typ = "sata"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    @property
    def floppy(self):
        typ = "floppy"
        name = "Default {!r} Controller".format(typ)
        obj = self.getControoler(name)
        if not obj:
            obj = self.createController(name, typ)
        return obj

    def onInfoUpdate(self):
        super(VM, self).onInfoUpdate()
        nameFields = [el for el in self.info.keys() if el.startswith("storagecontrollername")]
        if nameFields:
            idRe = re.compile(r"^storagecontrollername(\d+)$")
            ids = []
            for str in nameFields:
                match = idRe.match(str)
                ids.append(int(match.group(1)))

            destroyed = []
            for contr in self._controllers:
                if contr.idx in ids:
                    ids.remove(contr.idx)
                else:
                    # Controller is no longer part of VM
                    destroyed.append(contr)
            for el in destroyed:
                el.onDestroyed()
            for idx in ids:
                # New controllers
                self._controllers.append(StorageController(self, idx))

    def onStorageDestroyed(self, obj):
        self.refresh()

    def _getInfo(self):
        txt = self.cli.manage.showvminfo(self._initId)
        if txt:
            return OrderedDict(util.parseMachineReadableFmt(txt))
        else:
            return None