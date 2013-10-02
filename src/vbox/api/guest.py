import collections
import os
import re
import time

from . import (
    base,
    props,
)

class GuestControl(object):

    class Stats(object):
        file = "<vbox.api.GustControl.Stats.File>"
        directory = "<vbox.api.GustControl.Stats.Directory>"

    def __init__(self, interface, source, login, password):
        super(GuestControl, self).__init__()
        self.interface = interface
        self.source = source
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
        guestOs = self.interface.guest.osType
        if guestOs == "Linux":
            statFname = "/"
        else:
            raise NotImplementedError(guestOs)

        if timeout:
            endTime = time.time() + timeout
            timeOk = lambda: time.time() < endTime
        else:
            timeOk = lambda: True

        statRv = self.stat(statFname)[statFname]
        proceed = (statRv is None)
        while proceed:
            time.sleep(0.5)
            statRv = self.stat(statFname)[statFname]
            proceed = (statRv is None) and timeOk()

        return statRv is not None



    lastExecCall = 0

    def execute(self, program, environ=None, timeout=None, arguments=(),
        waitExit=True, stdout=True, stderr=True
    ):
        """Execute the target program on the guest.

        http://www.virtualbox.org/manual/ch08.html#vboxmanage-guestcontrol

        Params:
        `program` -- executable to be called
        `environ` -- dictionary of environment varaiables to be overriden for the guest process
            (pass `None` as value to delete the variable)
        `timeout` -- timeout (in seconds) for the host to wait for the guest to complete the program
        `arguments` -- extra command line arguments to be passed to the guest program
        `waitExit` -- wait for the gust program to complete before returning from the call
        `stdout` -- waits until the process ends and outputs and collects its stdout
        `stderr` -- waits until the process ends and outputs and collects its stderr
        """

        # It appears that `execute` freezes sometimes if call speed is too great.
        delay = max(0, time.time() - self.lastExecCall)
        if delay < 3:
            time.sleep(3 - delay)

        rv = self.source.guest.control.execute(program,
            user=self.login, password=self.password,
            environment=environ, timeout=timeout,
            arguments=tuple(arguments),
            waitExit=waitExit, waitStdout=stdout, waitStderr=stderr,
        )

        lastExecCall = time.time()
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