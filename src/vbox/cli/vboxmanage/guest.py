import re

from .. import (
    base,
    util,
)

class NoKwargCmd(base.SubCommand):

    def _toCmdLine(self, args, kwargs):
        assert not kwargs
        out = [self.__class__.__name__.lower()]
        out.extend(args)
        return tuple(out)

class GuestProperty(NoKwargCmd):

    enumRe = re.compile(
        r"^Name: (?P<name>.*), value: (?P<value>.*), timestamp: (?P<timestamp>.*), flags: ?(?P<flags>.*)$"
    )
    def enumerate(self, target):
        txt = self("enumerate", target)
        out = []
        for line in txt.splitlines():
            line = line.strip()
            if not line:
                continue
            match = self.enumRe.match(line)
            assert match, line
            out.append(match.groupdict())
        return out

class ConditionalOutCheck(util.OutCheck):
    """OutCheck that calls sub-outChecks depending on the filter outcome."""

    def __init__(self, subchecks):
        super(ConditionalOutCheck, self).__init__([])
        self.sub = tuple(subchecks)

    def __call__(self, args, rc, out):
        for (isValid, check) in self.sub:
            if isValid(args):
                return check(args, rc, out)
        raise NotImplementedError((args, rc, out))


class GuestControl(NoKwargCmd):

    copyToFmt = util.Formatter(
        all=("target", "src", "dest", "username", "password", "dryrun", "follow", "recursive", "verbose"),
        mandatory=("target", "src", "dest", "username", ),
        flags=("dryrun", "follow", "recursive", "verbose"),
        positional=("{target}", "copyto", "{src}", "{dest}"),
    )

    outCheck = ConditionalOutCheck([
        [(lambda cmd: cmd[2] == "stat"), util.OutCheck(okRc=(0, 1))], # 'stat' returns rc 1 when at least one of file names provided was not found.
        [(lambda cmd: True), util.OutCheck(okRc=(0, ))], # Default catcher
    ])
    
    def copyTo(self, *args, **kwargs):
        return self(*self.copyToFmt(args, kwargs))

    def execute(self, target, image, username, password, environment=None, timeout=None, arguments=None,
        waitExit=None, waitStdout=None, waitStderr=None
    ):
        cmd = [target, "execute", "--image", image, "--username", username, "--password", password]
        if environment:
            cmd.extend(("--environment", environment))
        if timeout:
            cmd.extend(("--timeout", str(timeout)))
        if waitExit:
            cmd.append("--wait-exit")
        if waitStdout:
            cmd.append("--wait-stdout")
        if waitStderr:
            cmd.append("--wait-stderr")
        if arguments:
            cmd.append("--")
            cmd.extend(arguments)
        return self(*cmd)

    statRe = re.compile('^Element "([^"]+)" found: Is a (\w+)$')
    def stat(self, target, files, username, password):
        cmd = [target, "stat"]
        cmd.extend(files)
        cmd.extend(("--username", username))
        cmd.extend(("--password", password))
        txt = self(*cmd)
        out = {}
        for line in txt.splitlines():
            match = self.statRe.match(line.strip())
            if match:
                out[match.group(1)] = match.group(2)
        return out