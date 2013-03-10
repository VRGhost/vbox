from distutils.spawn import find_executable

import os
import subprocess

class Command(object):
    """Python representation of VboxManage executable."""

    lock = property(lambda s: s.vb.cli._Lock)

    def __init__(self, vb, executable):
        self.vb = vb
        self._executable = find_executable(executable)
        if (not self._executable) or (not os.path.isfile(self._executable)):
            raise Exception("Failed to locate virtualbox executable {!r}".format(executable))

    def getCmd(self, tail):
        cmd = [self._executable]
        for el in tail:
            if not isinstance(el, basestring):
                el = str(el)
            cmd.append(el)
        return cmd

    def call(self, tail):
        cmd = self.getCmd(tail)
        with self.lock:
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=None)
            stdout = ""
            while proc.poll() is None:
                (out, err) = proc.communicate()
                assert err is None
                stdout += out
        assert proc.returncode is not None
        return (proc.returncode, cmd, stdout)

    def checkOutput(self, tail, okRc=(0, )):
        (rc, cmd, out) = self.call(tail)
        
        if rc in okRc:
            return stdout
        else:
            raise subprocess.CalledProcessError(rc, cmd, stdout)

    def popen(self, tail, **kwargs):
        with self.lock:
            print self.getCmd(tail)
            return subprocess.Popen(self.getCmd(tail), **kwargs)