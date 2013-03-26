"""VM extra data manager"""

from . import base

class ExtraData(base.VmElement):
    
    def setProp(self, name, value):
        if self.info:
            try:
                isNotSame = (self.info[name] != value)
            except KeyError:
                isNotSame = True
        else:
            isNotSame = True

        if isNotSame:
            self.cli.manage.setextradata(self.vm.getId(), name, value)
            self.updateInfo(force=True)

    def rmProp(self, name):
        self.cli.manage.setextradata(self.vm.getId(), name, "")
        self.updateInfo(force=True)        

    def _getInfo(self):
        return self.cli.manage.getextradata(self.vm.getId())

    def __setitem__(self, name, value):
        return self.setProp(name, value)

    def __getitem__(self, name):
        return self.info[name]

    def __delitem__(self, name):
        return self.rmProp(name)