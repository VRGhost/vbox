from collections import defaultdict
from distutils.spawn import find_executable
import weakref

import os
import subprocess

from .. import base

class TrailingCmd(base.VirtualBoxElement):

    head = None
    changesVmState = False

    def __init__(self, *args, **kwargs):
        super(TrailingCmd, self).__init__(*args, **kwargs)
        self._refs = defaultdict(list)

    def getCmd(self, tail):
        cmd = [self.head]
        cmd.extend(tail)
        return tuple(cmd)

    def call(self, tail):
        raise NotImplementedError

    def popen(self, tail, **kwargs):
        raise NotImplementedError

    def checkOutput(self, tail):
        raise NotImplementedError

    def addPreCmdExecListener(self, cb):
        return self._addRef("pre", cb)

    def _callPreCmdExec(self, cmd):
        self._callRefs("pre", cmd=cmd)

    def _callRefs(self, name, **kwargs):
        kwargs["source"] = self
        toRm = []
        for el in self._refs[name]:
            if len(el) == 2:
                (objRef, fnCb) = el
                obj = objRef()
                if obj is None:
                    toRm.append(el)
                    continue
                cb = lambda *a, **kw: fnCb(obj, *a, **kw)
            else:
                assert len(el) == 1
                cb = el[0]()
                if cb is None:
                    toRm.append(el)
                    continue

            cb(**kwargs)

        for el in toRm:
            self._rmRef(name, el)

    def _addRef(self, name, cb):
        try:
            obj = cb.im_self
            cb = cb.im_func
        except AttributeError:
            # Not bound method
            ref = (weakref.ref(cb), )
        else:
            ref = (weakref.ref(obj), cb)

        self._refs[name].append(ref)
        return lambda: self._rmRef(name, ref)

    def _rmRef(self, name, ref):
        self._refs[name].remove(ref)

class Command(TrailingCmd):
    """Python representation of VboxManage executable."""

    lock = property(lambda s: s.parent.cliAccessLock)

    def __init__(self, parent, executable):
        super(Command, self).__init__(parent)
        self.head = find_executable(executable)
        if (not self.head) or (not os.path.isfile(self.head)):
            raise Exception("Failed to locate virtualbox executable {!r}".format(executable))

    def getCmd(self, tail):
        cmd = super(Command, self).getCmd(tail)
        rv = []
        for el in cmd:
            if not isinstance(el, basestring):
                el = str(el)
            rv.append(el)
        return tuple(rv)

    def call(self, tail):
        with self.lock:
            (cmd, proc) = self.popen(tail,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=None
            )
            stdout = ""
            while proc.poll() is None:
                (out, err) = proc.communicate()
                assert err is None
                stdout += out
        assert proc.returncode is not None
        return (proc.returncode, cmd, stdout)

    def checkOutput(self, tail, okRc=(0, )):
        (rc, cmd, out) = self.call(tail)
        
        if rc == 0:
            return stdout
        else:
            raise subprocess.CalledProcessError(rc, cmd, stdout)

    def popen(self, tail, **kwargs):
        cmd = self.getCmd(tail)
        with self.lock:
            self._callPreCmdExec(cmd)
            proc = subprocess.Popen(cmd, **kwargs)
        return (cmd, proc)