import collections
import functools
import re
import threading
import time

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

def rateLimited(func):
    @functools.wraps(func)
    def _wrapper(self, *args, **kwargs):
        with self.rateLock:
            windowSize = time.time() - self._callLog[0]
            if windowSize < self.callsPerSec:
                time.sleep(self.callsPerSec - windowSize)
            try:
                return func(self, *args, **kwargs)
            finally:
                self._callLog.append(time.time())
    return _wrapper

class CallRateLimiter(object):
    """Context object that limits number of its invocation per moment of time."""

    def __init__(self, maxCallCnt, callsPerSec):
        super(CallRateLimiter, self).__init__()
        self.rateLock = threading.RLock()
        self.callLog = collections.deque([0], maxlen=maxCallCnt)
        self.callsPerSec = callsPerSec

    def acquire(self):
        self.rateLock.acquire()
        windowSize = time.time() - self.callLog[0]
        if windowSize < self.callsPerSec:
            time.sleep(max(self.callsPerSec - windowSize, 0.1))

    def release(self):
        self.rateLock.release()
        self.callLog.append(time.time())

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

class GuestControl(NoKwargCmd):
    """GuestControl binding.

    This object implements simple rate limiting
    because VBoxManage likes to exceed the number of guest sessions, supposingly because
    the sessions are garbage-collected at certain (rather low) frequency.
    """
    

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

    # The call rate is limited at maxCallCnt per callsPerSec
    maxCallCnt = 5
    callsPerSec = 1

    def __init__(self, *args, **kwargs):
        super(GuestControl, self).__init__(*args, **kwargs)
        self._rateLimiter = CallRateLimiter(self.maxCallCnt, self.callsPerSec)

    def __call__(self, *args, **kwargs):
        with self._rateLimiter:
            return super(GuestControl, self).__call__(*args, **kwargs)

    def copyTo(self, *args, **kwargs):
        return self(*self.copyToFmt(args, kwargs))

    def execute(self, target, image, username, password, environment=None, timeout=None, arguments=None,
        waitExit=None, waitStdout=None, waitStderr=None
    ):
        cmd = [target, "execute", "--image", image, "--username", username, "--password", password]
        kw = {}

        if environment:
            cmd.extend(("--environment", environment))
        if timeout:
            cmd.extend(("--timeout", str(timeout)))
            kw["_timeout"] = float(timeout) / 1000 # python timeouts are maesured in seconds

        if waitExit:
            cmd.append("--wait-exit")
        if waitStdout:
            cmd.append("--wait-stdout")
        if waitStderr:
            cmd.append("--wait-stderr")
        if arguments:
            cmd.append("--")
            cmd.extend(arguments)

        return self(*cmd, **kw)

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

    _maxGuestSessionRe = re.compile(r"Maximum number of guest sessions \((\d+)\) reached")
    def _onErrOutput(self, args, cmd, rc, out):
        match = self._maxGuestSessionRe.search(out)
        if match:
            raise self.exceptions.TooManyGuestSessions(int(match.group(1)))
        else:
            return super(GuestControl, self)._onErrOutput(args, cmd, rc, out)