import os

from .. import base

class HDD(base.VirtualBoxMedium):
    """HDD image."""

    size = property(lambda s: s.cli.util.toMBytes(s.getProp("Logical size")))
    used = property(lambda s: s.cli.util.toMBytes(s.getProp("Current size on disk")))

    fname = property(lambda s: s.getProp("Location"))
    formatVariant = property(lambda s: s.getProp("Format variant"))
    format = property(lambda s: s.getProp("Storage format"))
    accessible = property(lambda s: s.getProp("Accessible") == "yes")
    type = property(lambda s: s.getProp("Type"))
    name = property(lambda s: os.path.splitext(os.path.basename(s.fname))[0])

    def destroy(self):
        if not self.exists():
            return True
        os.unlink(self.fname)
        del self.info
        return True

    def exists(self):
        fname = self.fname
        return fname and os.path.isfile(fname)

    def clone(self, *args, **kwargs):
        return self.vb.hdds.clone(self._initId, *args, **kwargs)

    def getProp(self, name, default=None):
        if self.info:
            return self.info.get(name, default)
        else:
            return default

    def getVmAttachMedium(self):
        return self.fname

    def getVmAttachType(self):
        return "hdd"

    def _getInfo(self):
        out = self.vb.cli.manage.showhdinfo(self._initId)
        if out:
            return self.cli.util.parseParams(out)
        else:
            return None