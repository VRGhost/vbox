from .. import base

VmElement = base.VmElement

class DeverativeInfo(base.InfoKeeper):
    vm = property(lambda s: s.parent.vm)
    cli = property(lambda s: s.parent.cli)

    _parentInfo = None
    @property
    def info(self):
        if self.parent.info != self._parentInfo:
            self.updateInfo(force=True)
            self._parentInfo = self.parent.info.copy()
        return super(DeverativeInfo, self).info