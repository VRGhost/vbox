import os

from . import base

from .cli import util

class HDD(base.VirtualBoxMedium):
    """HDD image."""

    size = property(lambda s: util.toMBytes(s.getProp("Logical size")))
    used = property(lambda s: util.toMBytes(s.getProp("Current size on disk")))

    fname = property(lambda s: s.getProp("Location"))
    formatVariant = property(lambda s: s.getProp("Format variant"))
    format = property(lambda s: s.getProp("Storage format"))
    accessible = property(lambda s: s.getProp("Accessible") == "yes")
    type = property(lambda s: s.getProp("Type"))

    def destroy(self):
        if not self.exists():
            return True
        os.unlink(self.fname)
        del self.info
        return True

    def exists(self):
        fname = self.fname
        return fname and os.path.isfile(fname)

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
            return util.parseParams(out)
        else:
            return None