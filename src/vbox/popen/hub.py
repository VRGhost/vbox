from cStringIO import StringIO
import errno
import logging
import os
import subprocess
import tempfile
import threading
import time
import traceback
import warnings

try:
    import psutil
except ImportError:
    warnings.warn("No `psutil` module found, popen termination exception might be inconclusive.")
    psutil = None

from .. import exceptions
from . import exceptions as local_exceptions

from distutils.spawn import find_executable

log = logging.getLogger(__name__)

class BoundExecutable(object):

    terminateTimeout = 2 # Delay between terminated process is killed with SIGKILL
    killTimeout = 15 # Delay between kill is issued and the internal exception is raised.

    def __init__(self, hub, name):
        super(BoundExecutable, self).__init__()
        self.hub = hub
        self.name = name
        self.executable = find_executable(name, hub.root)
        if not self.executable:
            raise RuntimeError("{!r} not found in {!r}.".format(self.executable, self.hub))

    def __call__(self, cmd, timeout=None):
        realCmd = [self.executable]
        realCmd.extend(cmd)
        realCmd = tuple(realCmd)
        with self.hub.lock:
            with tempfile.NamedTemporaryFile() as fobj:
                proc = subprocess.Popen(
                    args=realCmd,
                    stderr=subprocess.STDOUT,
                    stdout=fobj,
                    universal_newlines=True,
                )
 
                if not self.procWait(proc, timeout):
                    # There was a timeout set and the subprocess is still alive
                    try:
                        proc.terminate()
                    except OSError as err:
                        if err.errno == errno.EACCES:
                            # on Windows attempting to terminate process that is already dead will cause 'access denied' exception
                            pass
                        else:
                            raise

                    if not self.procWait(proc, self.terminateTimeout):
                        # terminate signal failed.
                        # timeout passed, `proc` is still alive
                        try:
                            proc.kill()
                        except OSError as err:
                            if err.errno == errno.EACCES:
                                # on Windows attempting to terminate process that is already dead will cause 'access denied' exception
                                pass
                            else:
                                raise
                        
                        if not self.procWait(proc, self.killTimeout):
                            raise local_exceptions.PopenError("Unable to terminate/kill {!r}".format(cmd))
                
                    raise local_exceptions.TimeoutException(cmd)

                fobj.seek(0, 0)
                out = fobj.read()
                returncode = proc.poll()
                if returncode is None:
                    # Something went bad in the code
                    returncode = float("Inf")

        return (realCmd, returncode, out)

    def isProcRunning(self, proc):
        isRunning1 = proc.poll() is None
        if psutil:
            isRunning2 = psutil.pid_exists(proc.pid)
        else:
            isRunning2 = True

        return isRunning1 and isRunning2

    def procWait(self, proc, timeout):
        if timeout:
            endTime = time.time() + timeout
            while time.time() < endTime:
                if self.isProcRunning(proc):
                    time.sleep(0.5)
                else:
                    # Monitored process terminated
                    break
            else:
                # No 'break', return 'False' if exit is by timeout
                return not self.isProcRunning(proc)
        else:
            proc.wait()
        
        return True



    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.executable)

class BoundVerboseExecutable(BoundExecutable):

    def __call__(self, cmd, **kwargs):
        log.debug("Executing {} {}".format(self.executable, cmd))
        return super(BoundVerboseExecutable, self).__call__(cmd, **kwargs)


class BoundDebugExecutable(BoundVerboseExecutable):

    prev = None

    def __call__(self, cmd, **kwargs):
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
        return super(BoundDebugExecutable, self).__call__(cmd, **kwargs)


class Hub(object):

    root = None

    def __init__(self, root, debug, verbose):
        super(Hub, self).__init__()

        self.root = os.path.realpath(root)
        if not find_executable("VBoxManage", root):
            raise exceptions.VirtualBoxNotFound(root)

        self.lock = threading.Lock()
        self.debug = debug
        self.verbose = verbose

    def bind(self, executableName):
        if self.debug:
            rv = BoundDebugExecutable(self, executableName)
        elif self.verbose:
            rv = BoundVerboseExecutable(self, executableName)
        else:
            rv = BoundExecutable(self, executableName)
        return rv

    def __repr__(self):
        return "<{!r} {!r}>".format(self.__class__.__name__, self.root)