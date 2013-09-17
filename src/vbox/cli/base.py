import collections
import os

from . import (
    util,
    exceptions,
)

class BaseCmd(object):

    prefix = ()
    # Callable object that accepts (args, output) arguments as input and returns parsed structure.
    parser = util.parsers.Dummy()
    formatter = None # callable that maps arguments it is passed to the command line args (e.g. util.Formatter)
     # callable that returns 'False' if given output should raise exception (e.g. util.OutCheck)
    outCheck = util.OutCheck(okRc=(0, ))

    def __init__(self, interface):
        super(BaseCmd, self).__init__()
        self.interface = interface

    def __call__(self, *args, **kwargs):
        """Main command handler."""
        args = self._toCmdLine(args, kwargs)
        (cmd, rc, out) = self._exec(args)
        cmd = tuple(cmd)
        self._checkErrOutput(args, cmd, rc, out)
        return self._parse(args, out)

    def _parse(self, args, output):
        return self.parser(args, output)

    def _toCmdLine(self, args, kwargs):
        """Format call arguments to the command line argruments."""
        return self.formatter(args, kwargs)

    def _checkErrOutput(self, args, cmd, rc, out):
        if not self.outCheck(args, rc,  out):
            raise exceptions.CalledProcessError(cmd, rc, out)

    def _exec(self, cmd):
        """Execute command line command provided."""
        raise NotImplementedError

class RealCommand(BaseCmd):
    """Python representation of VboxManage executable."""

    def __init__(self, interface, executable):
        super(RealCommand, self).__init__(interface)
        self.subproc = interface.popen.bind(executable)

    def _exec(self, cmd):
        return self.subproc(cmd)

    def childCall(self, cmd):
        return self._exec(cmd)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.subproc)

class SubCommand(BaseCmd):

    def __init__(self, interface, parent):
        super(SubCommand, self).__init__(interface)
        self.parent = parent

    def _exec(self, cmd):
        return self.parent.childCall(cmd)

    def __repr__(self):
        return "<{} parent={!r}>".format(self.__class__.__name__, self.parent)