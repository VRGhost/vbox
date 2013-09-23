import functools
from functools import partial

from . import (
    base,
    exceptions,
)

refreshing = base.refreshing
refreshingLib = base.refreshingLib

class VM(base.Entity):

    info = base.refreshedProperty(lambda s: s.cli.manage.showVMInfo(s.id))

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.addCacheUpdateCallback(self._bindImmutableData)

    @refreshing
    def create(self, **kwargs):
        realKw = {
            "register": True,
        }
        realKw.update(kwargs)
        self.cli.manage.createVM(name=self.id, **realKw)
        if realKw["register"]:
            self.library.clearCache()

    @refreshingLib
    def unregister(self, delete=True):
        self.cli.manage.unregisterVM(self.id, delete=delete)
        self.library.pop(self)

    @refreshingLib
    def register(self):
        if self._configFile:
            self.cli.manage.registerVM(self._configFile)

    @refreshingLib
    def destroy(self):
        self.unregister(True)

    storageCtl = refreshing(lambda s, **kw: s.cli.manage.storageCtl(s.id, **kw))
    storageAttach = refreshing(lambda s, **kw: s.cli.manage.storageAttach(s.id, **kw))
    modify = refreshing(lambda s, **kw: s.cli.manage.modifyVM(s.id, **kw))

    start = refreshing(lambda s, **kw: s.cli.manage.startVM(s.id, **kw))
    savestate = refreshing(lambda s: s.cli.manage.controlVM.savestate(s.id))
    poweroff = refreshing(lambda s: s.cli.manage.controlVM.poweroff(s.id))
    reset = refreshing(lambda s: s.cli.manage.controlVM.reset(s.id))
    resume = refreshing(lambda s: s.cli.manage.controlVM.resume(s.id))
    pause = refreshing(lambda s: s.cli.manage.controlVM.pause(s.id))

    def onCliCallError(self, err):
        if isinstance(err, self.cli.exceptions.ParsedVboxError) \
        and ("NOT_FOUND" in err.errorName.upper()) \
        and (self.id in err.msg):
            raise exceptions.VmNotFound(self.id)


    def is_(self, challange):
        if super(VM, self).is_(challange):
            return True
        try:
            if self.info["UUID"] == challange:
                return True
        except KeyError:
            pass

        return False

    _configFile = None
    def _bindImmutableData(self, subj):
        assert subj is self
        cfg = self.info.get("CfgFile", None)
        if None not in (self._configFile, cfg):
            assert self._configFile == cfg, (self._configFile, cfg)
        else:
            self._configFile = cfg

class Library(base.Library):

    entityCls = VM

    @base.refreshed
    def listRegistered(self):
        out = []
        for (name, uuid) in self.cli.manage.list.vms().items():
            out.append(self.getOrCreate(uuid))
        return tuple(out)