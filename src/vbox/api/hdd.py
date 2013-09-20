import itertools
import os

from . import (
    base,
    props,
)

class HDD(base.Entity):
    """Virtual machine entity."""

    UUID = props.SourceStr(lambda s: s.source.info.get("UUID"))
    location = props.SourceStr(lambda s: s.source.info.get("Location"))
    size = props.HumanReadableFileSize(lambda s: s.source.info.get("Current size on disk"))
    maxSize = props.HumanReadableFileSize(lambda s: s.source.info.get("Logical size"))

    registered = props.SourceProperty(
        fget=lambda s: s.library.isRegistered(s),
        fset=lambda s, v: s.source.register() if v else s.source.unregister(delete=False),
        getDepends=lambda s: (s, s.library),
    )

    def destroy(self):
        if self.registered:
            self.source.unregister(delete=True)
        else:
            self.source.unlink()

class Library(base.Library):

    entityCls = HDD

    def new(self, filename, size):
        """Create new virtual machine with name `name`."""
        src = self._source.new(size=size)
        if not self._source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src)

    def createNew(self, size, targetDir=None, basename="unnamed_hdd"):
        if not targetDir:
            targetDir = self.interface.host.defaultVmDir

        def name_gen():
            yield basename
            for idx in itertools.count(1):
                yield "{}_{}".format(basename, idx)

        for name in name_gen():

            hddSource = self.source.new(
                os.path.join(targetDir, name),
            )
            try:
                hddSource.create(size=size)
            except hddSource.exceptions.FileAlreadyExists:
                continue

            return self.entityCls(hddSource, self)