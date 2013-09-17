from . import vm

class Objective(object):

    def __init__(self, cli):
        super(Objective, self).__init__()
        self.cli = cli

        self.vms = vm.Library(self)