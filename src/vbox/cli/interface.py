import threading

from .vboxmanage import VBoxManage

from . import util, exceptions

class CommandLineInterface(object):

    exceptions = exceptions
    
    def __init__(self, popen):
        super(CommandLineInterface, self).__init__()
        
        self.popen = popen
        self.manage = VBoxManage(self)
        self.util = util

    def __repr__(self):
        return "<{!r} for {!r}>".format(self.__class__.__name__, self.popen)