from cStringIO import StringIO
import logging
import os
import subprocess
import threading
import traceback

from .. import exceptions

from distutils.spawn import find_executable

log = logging.getLogger(__name__)

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

class BoundDebugExecutable(BoundExecutable):

    prev = None

    def __call__(self, cmd):
        cmd = tuple(cmd)

        fobj = StringIO()
        traceback.print_stack(file=fobj)
        fobj.seek(0, 0)
        tb = fobj.read()

        if self.prev:
            (prevCmd, prevTb) = self.prev
            if prevCmd == cmd:
                log.info("Prev traceback:\n\n{}\n\n".format(prevTb))
                log.info("Cur traceback:\n\n{}\n\n".format(tb))
                raise AssertionError("Duplicate successive commands: {}".format(cmd))
        self.prev = (cmd, tb)
        log.debug("Executing {} {}".format(self.executable, cmd))
        return super(BoundDebugExecutable, self).__call__(cmd)

class Hub(object):

    root = None

    def __init__(self, root, debug):
        super(Hub, self).__init__()

        self.root = os.path.realpath(root)
        if not find_executable("VBoxManage", root):
            raise exceptions.VirtualBoxNotFound(root)

        self.lock = threading.Lock()
        self.debug = debug

    def bind(self, executableName):
        if self.debug:
            rv = BoundDebugExecutable(self, executableName)
        else:
            rv = BoundExecutable(self, executableName)
        return rv

    def __repr__(self):
        return "<{!r} {!r}>".format(self.__class__.__name__, self.root)