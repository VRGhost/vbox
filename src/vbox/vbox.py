import logging
import os
import sys

from . import (
    bound,
    cli,
    exceptions,
    popen,
)

log = logging.getLogger(__name__)

class VBox(object):

    installRoot = None # Will contain path that

    def __init__(self, extraPath=None):
        """`extraPath` - list of extra directories to check for the virtualbox executables."""
        toCheck = []
        if extraPath:
            toCheck.extend(extraPath)
        toCheck.extend(sys.path)

        # assemble layers
        self.popen = self._findInstall(toCheck)
        self.cli = cli.CommandLineInterface(self.popen)
        self.bound = bound.VirtualBox(self.cli)
        # end layer assembly
        self.installRoot = self.popen.root

    def _findInstall(self, dirs):
        for testDir in dirs:
            if os.path.isdir(testDir):
                try:
                    return popen.Hub(testDir)
                except exceptions.VirtualBoxNotFound:
                    continue
            else:
                log.warning("{!r} is not a directory.".format(testDir))
        else:
            # No 'return' suceeded.
            raise exceptions.VirtualBoxNotFound(
                "None of the directories {!r} contains virtualbox installation.".format(dirs))

    def __repr__(self):
        return "<{} installRoot={!r}>".format(self.__class__.__name__, self.installRoot)