import threading

from .. import base

from .vboxHeadless import VBoxHeadless
from .vboxManage import VBoxManage

class CommandLineInterface(base.VirtualBoxElement):
    
    def __init__(self, *args, **kwargs):
        super(CommandLineInterface, self).__init__(*args, **kwargs)
        self.cliAccessLock = threading.RLock()
        self.manage = VBoxManage(self)
        self.headless = VBoxHeadless(self)
        self.programs = (
            self.manage,
            self.headless,
        )

    def addPreCmdExecListener(self, cb):
        _cancellers = [exc.addPreCmdExecListener(cb)
            for exc in self.programs]
        return lambda: [fn() for fn in _cancellers]