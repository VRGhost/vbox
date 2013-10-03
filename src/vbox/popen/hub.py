from cStringIO import StringIO
import errno
import logging
import os
import subprocess
import threading
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

class _PipeReader(threading.Thread):

    def __init__(self, pipe):
        super(_PipeReader, self).__init__()
        self.pipe = pipe
        self.output = ""
        self.daemon = True
        self.terminated = False

    def run(self):
        while not self.terminated:
            try:
                read = self.pipe.read(512)
            except (OSError, IOError) as err:
                if err.errno == errno.EINTR:
                    continue
                else:
                    raise

            if read:
                self.output += read
            else:
                # Pipe closed
                break

class BoundExecutable(object):

    terminateTimeout = 2 # Delay between terminated process is killed with SIGKILL instead
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
            proc = subprocess.Popen(
                args=realCmd,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            reader = _PipeReader(proc.stdout)

            def isProcRunning():
                isRunning1 = proc.poll() is None
                if psutil:
                    isRunning2 = psutil.pid_exists(proc.pid)
                else:
                    isRunning2 = True

                return isRunning1 and isRunning2

            reader.start()
            reader.join(timeout)
            if timeout and isProcRunning():
                # There was a timeout set and the subprocess is still alive
                try:
                    proc.terminate()
                except OSError as err:
                    if err.errno == errno.EACCES:
                        # on Windows attempting to terminate process that is already dead will cause 'access denied' exception
                        pass
                    else:
                        raise

                reader.join(self.terminateTimeout)
                if isProcRunning():
                    # timeout passed, `proc` is still alive
                    try:
                        proc.kill()
                    except OSError as err:
                        if err.errno == errno.EACCES:
                            # on Windows attempting to terminate process that is already dead will cause 'access denied' exception
                            pass
                        else:
                            raise

                    reader.join(self.killTimeout)

                    if isProcRunning():
                        raise local_exceptions.PopenError("Unable to terminate/kill {!r}".format(cmd))
                # Here, it is assumed that the subprocess is no longer alive
                reader.terminated = True
                reader.join(self.terminateTimeout)
                assert not reader.isAlive(), "Reader should really, really be dead by now. There should be no way it goes to the infinite loop."

                raise local_exceptions.TimeoutException(cmd)

            elif not timeout:
                proc.wait()

        out = reader.output
        returncode = proc.poll()
        if returncode is None:
            # Something went bad in the code
            returncode = float("Inf")

        return (realCmd, returncode, out)


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