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

class GuestControl(NoKwargCmd):

    copyToFmt = util.Formatter(
        all=("target", "src", "dest", "username", "password", "dryrun", "follow", "recursive", "verbose"),
        mandatory=("target", "src", "dest", "username", ),
        flags=("dryrun", "follow", "recursive", "verbose"),
        positional=("{target}", "copyto", "{src}", "{dest}"),
    )
    
    def copyTo(self, *args, **kwargs):
        return self(*self.copyToFmt(args, kwargs))