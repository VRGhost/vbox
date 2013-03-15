import collections
from distutils.spawn import find_executable
import os
import subprocess
import weakref

from .. import base
from .popen import Popen

VirtualBoxElement = base.VirtualBoxElement

class CliVirtualBoxElement(VirtualBoxElement):
    cliAccessLock = property(lambda s: s.parent.cliAccessLock)

class TrailingCmd(CliVirtualBoxElement):

    head = None
    changesVmState = False

    def __init__(self, *args, **kwargs):
        super(TrailingCmd, self).__init__(*args, **kwargs)
        self._refs = collections.defaultdict(list)

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

    def addPostCmdExecListener(self, cb):
        return self._addRef("post", cb)

    def _callPreCmdExec(self, cmd):
        self._callRefs("pre", cmd=cmd)

    def _callPostCmdExec(self, cmd, rc):
        self._callRefs("post", cmd=cmd, rc=rc)

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

    def __init__(self, parent, executable):
        super(Command, self).__init__(parent)
        self.head = find_executable(executable)
        if (not self.head) or (not os.path.isfile(self.head)):
            raise Exception("Failed to locate virtualbox executable {!r}".format(executable))

    def getCmd(self, tail):
        cmd = super(Command, self).getCmd(tail)
        return self.convertCmd(cmd)

    def convertCmd(self, cmd):
        rv = []
        for el in cmd:
            notString = not isinstance(el, basestring)

            if isinstance(el, collections.Iterable) and notString:
                el = ','.join(self.convertCmd(el))

            if notString:
                el = str(el)
            rv.append(el)
        return tuple(rv)

    def call(self, tail):
        with self.cliAccessLock:
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
        with self.cliAccessLock:
            self._callPreCmdExec(cmd)
            finishFn = lambda proc: self._callPostCmdExec(cmd, proc.returncode)
            proc = Popen(
                cmd, 
                onFinish=finishFn,
                **kwargs
            )
        return (cmd, proc)