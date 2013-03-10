import os
import time
import subprocess

from . import base

class VBoxHeadless(base.Command):
    
    def __init__(self, vb, executable="VBoxHeadless"):
        super(VBoxHeadless, self).__init__(vb, executable)

    def startvm(self, name, **kwargs):
        return self.popen(["--startvm", name], **kwargs)