import os
import time
import subprocess

from . import base

class VBoxHeadless(base.Command):

    changesVmState = True
    
    def __init__(self, parent, executable="VBoxHeadless"):
        super(VBoxHeadless, self).__init__(parent, executable)

    def startvm(self, name, **kwargs):
        return self.popen(["--startvm", name], **kwargs)