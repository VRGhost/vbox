import threading

from .. import base

from .vboxManage import VBoxManage

from . import util

class CommandLineInterface(base.VirtualBoxElement):
    
    def __init__(self, *args, **kwargs):
        super(CommandLineInterface, self).__init__(*args, **kwargs)
        self.cliAccessLock = threading.RLock()
        self.manage = VBoxManage(self)
        self.util = util
        self.programs = (
            self.manage,
        )

    def addPreCmdExecListener(self, cb):
        _cancellers = [exc.addPreCmdExecListener(cb)
            for exc in self.programs]
        return lambda: [fn() for fn in _cancellers]

    def addPostCmdExecListener(self, cb):
        _cancellers = [exc.addPostCmdExecListener(cb)
            for exc in self.programs]
        return lambda: [fn() for fn in _cancellers]