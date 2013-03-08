from distutils.spawn import find_executable
import os
import subprocess

from . import chgCmds, infoCmds
from .list import List


class VBoxManage(object):
    """Python representation of VboxManage executable."""

    list = createhd = None

    def __init__(self, executable="VBoxManage"):
        self._executable = find_executable(executable)
        if (not self._executable) or (not os.path.isfile(self._executable)):
            raise Exception("Failed to locate virtualbox executable {!r}".format(executable))

        self.list = List(self)
        self.showhdinfo = infoCmds.ShowHdInfo(self)
        self.showvminfo = infoCmds.ShowVmInfo(self)

        self.createhd = chgCmds.CreateHD(self)
        self.createvm = chgCmds.CreateVM(self)
        self.unregistervm = chgCmds.UnregisterVM(self)
        self.storagectl = chgCmds.StorageCtl(self)
        self.storageattach = chgCmds.StorageAttach(self)

    def checkOutput(self, tail, rc=0):
        cmd = [self._executable]
        cmd.extend(tail)
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            if err.returncode == rc:
                return err.output
            else:
                raise