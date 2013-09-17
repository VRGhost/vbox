import os
import threading
import subprocess

from .. import exceptions

from distutils.spawn import find_executable

class BoundExecutable(object):

    def __init__(self, hub, name):
        super(BoundExecutable, self).__init__()
        self.hub = hub
        self.name = name
        self.executable = find_executable(name, hub.root)
        if not self.executable:
            raise RuntimeError("{!r} not found in {!r}.".format(self.executable, self.hub))

    def __call__(self, cmd):
        realCmd = [self.executable]
        realCmd.extend(cmd)
        realCmd = tuple(realCmd)
        
        with self.hub.lock:
            proc = subprocess.Popen(
                args=realCmd,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            (out, err) = proc.communicate()
        assert not err
        return (realCmd, proc.returncode, out)


    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.executable)

class Hub(object):

    root = None

    def __init__(self, root):
        super(Hub, self).__init__()

        self.root = os.path.realpath(root)
        if not find_executable("VBoxManage", root):
            raise exceptions.VirtualBoxNotFound(root)

        self.lock = threading.Lock()

    def bind(self, executableName):
        return BoundExecutable(self, executableName)

    def __repr__(self):
        return "<{!r} {!r}>".format(self.__class__.__name__, self.root)