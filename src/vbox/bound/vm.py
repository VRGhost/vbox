from . import base

refreshing = base.refreshing

class VM(base.Entity):

    _info = None
    info = property(lambda s: s._info())

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)

        self._info = base.Caching(lambda: self.cli.manage.showVMInfo(self.id))

    def refresh(self):
        super(VM, self).refresh()
        self._info.refresh()

    @refreshing
    def create(self, **kwargs):
        realKw = {
            "register": True,
        }
        realKw.update(kwargs)
        self.cli.manage.createVM(name=self.id, **realKw)

    @refreshing
    def unregister(self, delete=True):
        self.cli.manage.unregisterVM(self.id, delete=delete)
        self.library.pop(self)

    def destroy(self):
        self.unregister(True)

    modify = refreshing(lambda s, **kw: s.cli.manage.modifyVM(s.id, **kw))

    start = refreshing(lambda s, **kw: s.cli.manage.startVM(s.id, **kw))
    savestate = refreshing(lambda s: s.cli.manage.controlVM.savestate(s.id))
    poweroff = refreshing(lambda s: s.cli.manage.controlVM.poweroff(s.id))
    reset = refreshing(lambda s: s.cli.manage.controlVM.reset(s.id))
    resume = refreshing(lambda s: s.cli.manage.controlVM.resume(s.id))
    pause = refreshing(lambda s: s.cli.manage.controlVM.pause(s.id))

class Library(base.Library):

    entityCls = VM