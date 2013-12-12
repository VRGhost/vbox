import logging
import os
import sys
import threading
import time

from . import (
    api,
    bound,
    cli,
    config,
    exceptions,
    popen,
)

log = logging.getLogger(__name__)

class TimeCounter(threading.Thread):

    resoultion = 2 # seconds

    def __init__(self, callback):
        super(TimeCounter, self).__init__(
            name="vbox.bound.interface.TimeCounter"
        )
        self._cb = callback
        self.daemon = True
        self.start()

    def run(self):
        while True:
            res = self.resoultion
            delta = res / 2.0

            start = time.time()
            time.sleep(res)
            end = time.time()
            period = end - start
            if (period < (res - delta)) or (period > (res + delta)):
                # Assume system time changed,
                # using fallback value for 'period'
                period = res
            self._cb(period)

class VBox(object):

    installRoot = None # Will contain path that

    def __init__(self, extraPath=None, debug=False, verbose=False):
        """`extraPath` - list of extra directories to check for the virtualbox executables.
            `debug` - runs bindings in the debugging mode, enables run-time sainity checks.
        """
        self.debug = debug
        self.verbose = verbose or debug

        toCheck = set()
        if extraPath:
            toCheck.update(extraPath)

        osPath = os.environ.get("PATH")
        if osPath:
            toCheck.update(osPath.split(os.pathsep))

        # assemble layers
        self.popen = self._findInstall(toCheck)
        self.cli = cli.CommandLineInterface(self.popen)
        self.bound = bound.VirtualBox(self.cli)
        self.api = api.VirtualBox(self.bound)
        self.config = config.VirtualBox(self.api)
        # end layer assembly
        self.installRoot = self.popen.root
        self._ticker = TimeCounter(self._onTimeTick)

    def _findInstall(self, dirs):
        for testDir in dirs:
            if os.path.isdir(testDir):
                try:
                    return popen.Hub(testDir, self.debug, self.verbose)
                except exceptions.VirtualBoxNotFound:
                    continue
            else:
                log.warning("{!r} is not a directory.".format(testDir))
        else:
            # No 'return' suceeded.
            raise exceptions.VirtualBoxNotFound(
                "None of the directories {!r} contains virtualbox installation.".format(dirs))

    @classmethod
    def fromDict(cls, data):
        return cls(**data)

    def _onTimeTick(self, period):
        for obj in (self.bound, self.api):
            obj.onTimeTick(period)

    def __repr__(self):
        return "<{} installRoot={!r}>".format(self.__class__.__name__, self.installRoot)