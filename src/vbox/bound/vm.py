import functools
from functools import partial

from . import (
    base,
    exceptions,
    extraData,
    guest,
)

refreshing = base.refreshing
refreshingLib = base.refreshingLib

class VM(base.Entity):

    extraData = None

    def __init__(self, *args, **kwargs):
        super(VM, self).__init__(*args, **kwargs)
        self.extraData = extraData.ExtraData(self.root.cli, self.id)
        self.guest = guest.Guest(self)

    @base.refreshedProperty
    def info(self):
        return self.cli.manage.showVMInfo(self.id)

    @base.refreshed
    def exists(self):
        try:
            self.info
        except self.exceptions.VmNotFound:
            rv = False
        else:
            rv = True
        return rv

    @refreshing
    def sharedFolder(self, **kwargs):
        self.cli.manage.sharedFolder(target=self.id, **kwargs)

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

    def clone(self, name, basedir, register=True):
        try:
            self.cli.manage.cloneVM(self.id,
                name=name, basefolder=basedir, register=register)
        finally:
            if register:
                self.library.clearCache()
        rv = self.library.new(name)
        rv.clearCache() # if this object had been existing already, its cache has to be reset
        # As it was not existing previously.
        assert rv.exists(), (rv, name)
        return rv

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

        for key in ("UUID", "name"):
            try:
                if self.info[key] == challange:
                    return True
            except KeyError:
                pass

        return False


    def onCacheUpdate(self, who):
        """An event callback that tells this object that
        another object had cleared its cache.
        """
        super(VM, self).onCacheUpdate(who)
        if who is self:
            self._bindImmutableData()

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