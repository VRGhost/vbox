import itertools
import os

from . import (
    base,
    props,
)

class HDD(base.Entity):
    """Virtual machine entity."""

    UUID = props.Str(lambda s: s.source.info.get("UUID"))
    location = props.Str(lambda s: s.source.info.get("Location"))
    size = props.HumanReadableFileSize(resultUnits="mbytes", fget=lambda s: s.source.info.getAny([
            "Size on disk", # VirtualBox 3.4
            "Current size on disk", # VirtualBox < 3.4
        ]))
    maxSize = props.HumanReadableFileSize(
        resultUnits="mbytes", fget=lambda s: s.source.info.getAny([
            "Capacity", # VirtualBox 3.4
            "Logical size", # VirtualBox < 3.4
        ]))
    #accessible = props.SourceProperty(lambda s: s.source.info.get("Accessible") == "yes")

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

    def getStorageAttachKwargs(self):
        return {
            "type": "hdd",
            "medium": self.location,
        }

class Library(base.Library):

    entityCls = HDD

    def fromFile(self, filename):
        if not os.path.isfile(filename):
            raise self.exceptions.MissingFile(filename)
        src = self.source.new(filename)
        return self.entityCls(src, self)

    def create(self, size, targetDir=None, basename="unnamed_hdd"):
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