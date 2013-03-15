"""manage subcommand."""

import subprocess
from . import base

class CmdError(subprocess.CalledProcessError):
    """Base class for command-line exceptions."""

    def __str__(self):
        return "{!r} failed with rc={} and output:\n=====\n{}\n========".format(
            self.returncode, self.cmd, self.output)

class Base(base.TrailingCmd):
    
    # Name that this subcommand maps to
    errClass = CmdError
    changesVmState = None

    def __init__(self, parent):
        super(Base, self).__init__(parent)
        # enforce `changesVmState` to be non-changable
        val = self.__class__.changesVmState
        if not isinstance(val, property):
            assert self.changesVmState in (True, False), self.changesVmState
            self.__class__.changesVmState = property(lambda s: val)

        if self.head == None:
            self.head = self.__class__.__name__.lower()

        self.parent.addPreCmdExecListener(self._onParentPreExec)
        self.parent.addPostCmdExecListener(self._onParentPostExec)

    def getRcHandlers(self):
        return {}

    def onError(self, rc, cmd, out):
        raise self.errClass(cmd, rc, out)

    def call(self, tail):
        return self.parent.call(self.getCmd(tail))

    def checkOutput(self, tail):
        (rc, cmd, out) = self.call(tail)
        handler = self.getRcHandlers().get(rc)
        if handler:
            return handler(cmd, out)
        elif rc != 0:
            return self.onError(rc, cmd, out)
        else:
            return out

    def _onParentPreExec(self, source, cmd):
        if self.head in cmd:
            self._callPreCmdExec(cmd)

    def _onParentPostExec(self, source, cmd, rc):
        if self.head in cmd:
            self._callPostCmdExec(cmd, rc)


class Generic(Base):
    """Generic command-line callable interface."""

    opts = ()
    flags = ()
    bools = ()
    mandatory = ()

    def dictToCmdLine(self, kwargs):
        cmd = []
        expecting = list(self.mandatory)
        
        long = self.opts
        flags = self.flags
        bools = self.bools

        for (name, value) in kwargs.iteritems():
            if value is None:
                continue
            cmdName = "--" + name
            if name in long:
                cmd.extend((cmdName, value))
            elif name in flags:
                if value:
                    cmd.append(cmdName)
            elif name in bools:
                if isinstance(value, basestring) and \
                    (value.lower() in ("on", "off")) \
                :
                    value = value.lower()
                else:
                    value = "on" if value else "off"
                cmd.extend((cmdName, value))
            else:
                raise TypeError("Unexpected option {!r}.".format(name))

            try:
                expecting.remove(name)
            except ValueError:
                pass

        if expecting:
            raise TypeError("Mandatory arguments {!r} not provided.".format(expecting))
        return cmd

    def __call__(self, **kwargs):
        return self.checkOutput(self.dictToCmdLine(kwargs))
            
class PlainCall(Base):
    """A command that trainslates to plain command line call, with no kwarg magic."""
  
    def __call__(self, *args):
        return self.checkOutput(args)

class ArgCmd(Generic):

    nargs = 1
    argnames = ()

    def __call__(self, *args, **kwargs):
        if len(args) != self.nargs:
            raise TypeError("{} arguments expected, {} provided.".format(
                self.nargs, len(args)))

        cmd = []
        for (pos, val) in enumerate(args):
            try:
                name = self.argnames[pos]
            except LookupError:
                name = None
            if name:
                cmd.append(name)
            cmd.append(val)

        kwCmd = self.dictToCmdLine(kwargs)

        cmd.extend(kwCmd)
        return self.checkOutput(cmd)