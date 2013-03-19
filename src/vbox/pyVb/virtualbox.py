import os
import re
import threading

from vbox import cli

from . import (
    base,
    info,
    vm,
    disks,
    network,
)

class VirtualBox(base.ElementGroup):
    """Python version of virtualbox program/service."""

    
    # Each object in this program should have pointer to the virtualbox object
    vb = property(lambda self: self)
    parent = cli = None

    def __init__(self):
        self.cli = cli.CommandLineInterface(self)
        self.info = info.Info(self)
        super(VirtualBox, self).__init__(self)

    def getElements(self):
        return {
            "vms": vm.VmLibrary(self),
            "hdds": disks.HddLibrary(self),
            "floppies": disks.FloppyLibrary(self),
            "dvds": disks.DvdLibrary(self),
            "net": network.NetworkLibrary(self),
        }