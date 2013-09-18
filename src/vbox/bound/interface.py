from . import vm

class VirtualBox(object):

    def __init__(self, cli):
        super(VirtualBox, self).__init__()
        self.cli = cli
        self.vms = vm.Library(self)