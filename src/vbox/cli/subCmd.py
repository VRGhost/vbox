"""manage subcommand."""

import subprocess

class Base(object):
    
    # Name that this subcommand maps to
    cmd = None

    def __init__(self, parent):
        self.parent = parent
        if self.cmd == None:
            self.cmd = self.__class__.__name__.lower()

    def getRcHandlers(self):
        return {}

    def checkOutput(self, tail, rc=0):
        cmd = [self.cmd]
        cmd.extend(tail)

        strCmd = []
        for el in cmd:
            if not isinstance(el, basestring):
                el = str(el)
            strCmd.append(el)

        handlers = self.getRcHandlers()
        try:
            out = self.parent.checkOutput(strCmd, rc)
        except subprocess.CalledProcessError as err:
            out = err.output
            myHandler = handlers.get(err.returncode)
            if not myHandler:
                raise
        else:
            myHandler = handlers.get(rc)

        if myHandler:
            out = myHandler(out)
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
