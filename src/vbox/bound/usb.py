from . import base

class Library(base.Library):

    @base.refreshed(maxCacheAge=4) # Cache for this property expires every 2 seconds
    def getHostDevices(self):
        return self.cli.manage.list.usbhost()