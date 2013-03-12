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

    def __init__(self, parent):
        super(Base, self).__init__(parent)
        if self.head == None:
            self.head = self.__class__.__name__.lower()

    def getRcHandlers(self):
        return {}

    def onError(self, rc, cmd, out):
        raise self.errClass(cmd, rc, out)

    def call(self, tail):
        cmd = self.getCmd(tail)
        self._callPreCmdExec(cmd)
        return self.parent.call(cmd)

    def checkOutput(self, tail):
        (rc, cmd, out) = self.call(tail)
        handler = self.getRcHandlers().get(rc)
        if handler:
            return handler(cmd, out)
        elif rc != 0:
            return self.onError(rc, cmd, out)
        else:
            return out


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

class VmCmd(Generic):

    def __call__(self, vmName, **kwargs):
        cmd = self.dictToCmdLine(kwargs)
        cmd.insert(0, vmName)
        return self.checkOutput(cmd)

class VmPropSetter(Generic):

    propName = None

    def __call__(self, vmName, propName, **kwargs):
        cmd = self.dictToCmdLine(kwargs)
        prefix = [vmName, propName]
        prop = self.propName
        if prop:
            prefix.insert(1, prop)
        return self.checkOutput(prefix + cmd)