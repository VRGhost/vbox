import collections
import os
import re
import time

from . import (
    base,
    props,
)

class GuestControl(base.SourceObjectProxy):

    class Stats(object):
        file = "<vbox.api.GustControl.Stats.File>"
        directory = "<vbox.api.GustControl.Stats.Directory>"

    def __init__(self, interface, source, login, password):
        super(GuestControl, self).__init__(source)
        self.interface = interface
        self.login = login
        self.password = password

    def copyTo(self, srcFile, outFile):
        assert os.path.isfile(srcFile)
        self.source.guest.control.copyTo(
            dest=outFile, src=srcFile,
            user=self.login, password=self.password
        )

    def stat(self, *paths):
        results = self.source.guest.control.stat(
            paths=paths,
            user=self.login, password=self.password,
        )
        out = {}
        for (name, value) in results.iteritems():
            if value is None:
                myValue = None
            elif value.lower() == "file":
                myValue = self.Stats.file
            elif value.lower() == "directory":
                myValue = self.Stats.directory
            else:
                raise NotImplementedError(value)
            out[name] = myValue
        return out

    def waitBoot(self, timeout=None):
        """Wait for the guest to boot its OS and for the guest additions to become operational."""
        guestOs = self.interface.guest.osType
        if guestOs == "Linux":
            filesThatMustExist = ("/", "/etc")

            testStr = "==42 hello world 24=="
            execProgs = [
                {
                    "call": ("/bin/echo", testStr),
                    "test": lambda out: testStr in out,
                },
            ]

            filesThatMustNotExist = ("/etc/nologin", )
        else:
            raise NotImplementedError(guestOs)

        if timeout:
            endTime = time.time() + timeout
            timeOk = lambda: time.time() < endTime
        else:
            timeOk = lambda: True

        filesReady = lambda: None not in self.stat(*filesThatMustExist).values()
        while (not filesReady()) and timeOk():
            time.sleep(0.5)

        if not timeOk():
            # Failed due to the timeout
            return False

        while timeOk():
            for prog in execProgs:
                try:
                    out = self.execute(prog["call"], timeout=1.5, retries=5)
                except self.exceptions.ExecuteError:
                    break

                if not prog["test"](out):
                    break
            else:
                # No 'break' called, all programs executed fine
                break

        if not timeOk():
            return False

        filesReady = lambda: all(el is None for el in self.stat(*filesThatMustNotExist).values())
        while (not filesReady()) and timeOk():
            time.sleep(0.5)

        # time.sleep(5)
        return timeOk()



    lastExecCall = 0

    def execute(self, arguments, environ=None, timeout=None, program=None,
        retries=None,
        waitExit=True, stdout=True, stderr=True
    ):
        """Execute the target program on the guest.

        http://www.virtualbox.org/manual/ch08.html#vboxmanage-guestcontrol

        Params:
        `environ` -- dictionary of environment varaiables to be overriden for the guest process
            (pass `None` as value to delete the variable)
        `timeout` -- timeout (in seconds) for the host to wait for the guest to complete the program
        `program` -- executable to be called, if empty, it is expected for the first element of `arguments`
            to contain the program (with absolute path)
        `arguments` -- extra command line arguments to be passed to the guest program
        `waitExit` -- wait for the gust program to complete before returning from the call
        `stdout` -- waits until the process ends and outputs and collects its stdout
        `stderr` -- waits until the process ends and outputs and collects its stderr
        `retries` -- maximum amount of re-attempts to execute the command if it fails.
        """

        # It appears that `execute` freezes sometimes if call speed is too great.
        delay = max(0, time.time() - self.lastExecCall)
        if delay < 2:
            time.sleep(2 - delay)

        if not program:
            if arguments:
                arguments = list(arguments)
                program = arguments.pop(0)
            else:
                raise self.exceptions.GuestException("Please provide program name to be executed")

        pendingExceptions = []
        if retries:
            if not timeout:
                raise Exception("You have to define timeout if you want to do retries.")
            tryCounter = xrange(retries)
        else:
            tryCounter = (0, )

        for attemptNo in tryCounter:
            try:
                rv = self.source.guest.control.execute(program,
                    user=self.login, password=self.password,
                    environment=environ, timeout=timeout,
                    arguments=tuple(arguments),
                    waitExit=waitExit, waitStdout=stdout, waitStderr=stderr,
                )
            except self.source.exceptions.ExecuteTimeout as err:
                pendingExceptions.append(self.exceptions.ExecuteTimeout(repr(err)))
            except self.source.cli.exceptions.CalledProcessError as err:
                pendingExceptions.append(self.exceptions.ExecuteError(repr(err)))
            else:
                # No exceptions
                break
            finally:
                self.lastExecCall = time.time()
        else:
            # No `break` called, attempts exausted
            assert pendingExceptions
            if len(pendingExceptions) == 1:
                raise pendingExceptions[0]
            else:
                raise self.exceptions.ExecuteError(" :: ".join(str(el) for el in pendingExceptions))

        return rv

    def __exit__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

class GuestAdditions(base.SourceObjectProxy):

    def __init__(self, interface):
        super(GuestAdditions, self).__init__(interface.source)
        self.interface = interface

    @props.SourceProperty
    def info(self):
        return self.source.guest.properties.all()

    @props.SourceProperty
    def net(self):
        netRe = re.compile(r"^/VirtualBox/GuestInfo/Net/(\d+)/(.*)$")
        data = collections.defaultdict(dict)

        for el in self.info:
            match = netRe.match(el["name"])
            if match:
                (idx, path) = match.groups()
                path = path.split('/')
                target = data[int(idx)]

                infix = path[:-1]
                while infix:
                    key = infix.pop(0)
                    target.setdefault(key, {})
                    target = target[key]

                target[path[-1]] = el["value"]

        keys = sorted(data.keys())
        rv = tuple(data[key] for key in keys)
        return rv

    @props.Str
    def osType(self):
        return self.find("/VirtualBox/GuestInfo/OS/Product")

    def find(self, name, outField="value"):
        for el in self.info:
            if el["name"] == name:
                return el[outField]
        return None

    def control(self, login, password):
        """Bound guest control object."""
        return GuestControl(self.interface, self.source, login, password)