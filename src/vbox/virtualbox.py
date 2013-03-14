import os
import re
import threading

from . import (
    base,
    cli, 
    hdd,
    info,
    vm,
    resources,
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
            "hdd": hdd.HddLibrary(self),
            "vms": vm.VmLibrary(self),
            "resources": resources.ResourceLibrary(self)
        }
