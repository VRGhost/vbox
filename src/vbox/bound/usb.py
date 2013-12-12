from . import base

class Library(base.Library):

    @base.refreshedProperty
    def hostDevices(self):
        return self.cli.manage.list.usbhost()