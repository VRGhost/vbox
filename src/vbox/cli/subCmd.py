"""manage subcommand."""

import subprocess

class CmdError(subprocess.CalledProcessError):
    """Base class for command-line exceptions."""

    def __str__(self):
        return "{!r} failed with rc={} and output:\n=====\n{}\n========".format(
            self.returncode, self.cmd, self.output)

class Base(object):
    
    # Name that this subcommand maps to
    cmd = None
    errClass = CmdError

    def __init__(self, parent):
        self.parent = parent
        if self.cmd == None:
            self.cmd = self.__class__.__name__.lower()

    def getRcHandlers(self):
        return {}

    def getCmd(self, tail):
        cmd = [self.cmd]
        cmd.extend(tail)
        return cmd

    def onError(self, rc, cmd, out):
        raise self.errClass(rc, cmd, stdout)

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


class Generic(Base):
    """Generic command-line callable interface."""

    longOpts = ()
    boolOpts = ()
    mandatory = ()

    def dictToCmdLine(self, kwargs):
        cmd = []
        expecting = list(self.mandatory)
        long = self.longOpts
        bools = self.boolOpts
        handlers = self.getRcHandlers()

        for (name, value) in kwargs.iteritems():
            if value is None:
                continue
            if name in long:
                if name in bools:
                    if value:
                        cmd.append("--" + name)
                else:
                    cmd.extend(("--" + name, value))
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

class VmPropSetter(Generic):

    def __call__(self, vmName, **kwargs):
        cmd = self.dictToCmdLine(kwargs)
        cmd.insert(0, vmName)
        return self.checkOutput(cmd)
