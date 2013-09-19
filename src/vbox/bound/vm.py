from . import base

refreshing = base.refreshing

class VM(base.Entity):

    info = base.refreshedProperty(lambda s: s.cli.manage.showVMInfo(s.id))

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)

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

    @refreshing
    def destroy(self):
        self.unregister(True)

    modify = refreshing(lambda s, **kw: s.cli.manage.modifyVM(s.id, **kw))

    start = refreshing(lambda s, **kw: s.cli.manage.startVM(s.id, **kw))
    savestate = refreshing(lambda s: s.cli.manage.controlVM.savestate(s.id))
    poweroff = refreshing(lambda s: s.cli.manage.controlVM.poweroff(s.id))
    reset = refreshing(lambda s: s.cli.manage.controlVM.reset(s.id))
    resume = refreshing(lambda s: s.cli.manage.controlVM.resume(s.id))
    pause = refreshing(lambda s: s.cli.manage.controlVM.pause(s.id))

    def is_(self, challange):
        if super(VM, self).is_(challange):
            return True
        try:
            if self.info["UUID"] == challange:
                return True
        except KeyError:
            pass

        return False

class Library(base.Library):

    entityCls = VM

    @base.refreshed
    def listRegistered(self):
        out = []
        for (name, uuid) in self.cli.manage.list.vms().items():
            out.append(self.getOrCreate(uuid))
        return tuple(out)