import collections
import os
import re

from . import (
    util,
    exceptions,
)

ERR_MSG_PARSE_RE = re.compile('\n'.join([
    r"^([^:]+): error: (?P<msg>.*)$",
    r"^(\1): error: Details: code (?P<str_code>\w+) \(0x(?P<hex_code>[0-9a-f]+)\)",
    ]), re.MULTILINE | re.IGNORECASE
)

class BaseCmd(object):

    exceptions = exceptions
    prefix = ()
    # Callable object that accepts (args, output) arguments as input and returns parsed structure.
    parser = util.parsers.Dummy()
    formatter = None # callable that maps arguments it is passed to the command line args (e.g. util.Formatter)
    # callable that returns 'False' if given output should raise exception (e.g. util.OutCheck)
    outCheck = util.OutCheck(okRc=(0, ))

    classNamePrefix = True # If this field is set to true, all generated command lines will be prefixed with the lowercase name of class.
    # This is for convinience only, as it is assumed that all objects declared on the CLI level will be have names of the appropriate CLI functions

    def __init__(self, interface):
        super(BaseCmd, self).__init__()
        self.interface = interface

    def __call__(self, *args, **kwargs):
        """Main command handler.

        All kwargs starting with '_' are passed to the `execute` call
        """
        execKw = {}
        for name in tuple(kwargs.keys()):
            if name.startswith("_"):
                execKw[name[1:]] = kwargs.pop(name)

        args = self._toCmdLine(args, kwargs)
        (cmd, rc, out) = self._exec(args, **execKw)
        cmd = tuple(cmd)
        self._checkErrOutput(args, cmd, rc, out)
        return self._parse(args, out)

    def _parse(self, args, output):
        return self.parser(args, output)

    def _toCmdLine(self, args, kwargs):
        """Format call arguments to the command line argruments."""
        rv = self.formatter(args, kwargs)
        if self.classNamePrefix:
            new = [self.__class__.__name__.lower()]
            new.extend(rv)
            rv = tuple(new)
        return rv

    def _checkErrOutput(self, args, cmd, rc, out):
        if not self.outCheck(args, rc, out):
            match = ERR_MSG_PARSE_RE.search(out)
            if match:
                raise self.exceptions.ParsedVboxError(
                    cmd, rc, out,
                    errorName=match.group("str_code").strip(),
                    errorCode=int(match.group("hex_code"), 16),
                    message=match.group("msg").strip(),
                )
            else:
                raise self.exceptions.CalledProcessError(cmd, rc, out)

    def _exec(self, cmd):
        """Execute command line command provided."""
        raise NotImplementedError

class RealCommand(BaseCmd):
    """Python representation of VboxManage executable."""

    def __init__(self, interface, executable):
        super(RealCommand, self).__init__(interface)
        self.subproc = interface.popen.bind(executable)

    def _exec(self, cmd, **kw):
        return self.subproc(cmd, **kw)

    def childCall(self, cmd, kw):
        return self._exec(cmd, **kw)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.subproc)

class SubCommand(BaseCmd):

    def __init__(self, interface, parent):
        super(SubCommand, self).__init__(interface)
        self.parent = parent

    def _exec(self, cmd, **kw):
        return self.parent.childCall(cmd, kw)

    def __repr__(self):
        return "<{} parent={!r}>".format(self.__class__.__name__, self.parent)