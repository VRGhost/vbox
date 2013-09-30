from . import base

class GuestEl(base.CliAccessor):

    def __init__(self, vm):
        super(GuestEl, self).__init__(vm.cli)
        self.vm = vm
        self.id = vm.id
        self.vm.addCacheClearCallback(self._onVmRefresh)

    def _onVmRefresh(self, vm):
        assert vm is self.vm
        self.clearCache()

class GuestProperties(GuestEl):

    @base.refreshed
    def all(self):
        return self.cli.manage.guestProperty.enumerate(self.id)

class GuestControl(GuestEl):

    def copyTo(self, src, dest, user, password="", dryrun=False, followSymlinks=True, recursive=False):
        return self.cli.manage.guestControl.copyTo(
            self.id, src, dest,
            username=user, password=password,
            dryrun=dryrun, follow=followSymlinks,
            recursive=recursive,
        )

class Guest(object):

    def __init__(self, vm):
        self.properties = GuestProperties(vm)
        self.control = GuestControl(vm)