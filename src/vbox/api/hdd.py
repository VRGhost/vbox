from . import base, props

class HDD(base.Entity):
    """Virtual machine entity."""

    UUID = props.SourceStr(lambda src: src.info.get("UUID"))

class Library(base.Library):

    entityCls = HDD

    def new(self, filename, size):
        """Create new virtual machine with name `name`."""
        src = self._source.new(size=size)
        if not self._source.isRegistered(src):
            src.create(register=True)
        return self.entityCls(src)