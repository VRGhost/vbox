from . import (
    base,
    props,
    exceptions,
)

class HostDevice(base.SubEntity):

    def __init__(self, parent, uuid):
        super(HostDevice, self).__init__(parent)
        self.UUID = uuid

class Library(base.Library):

    @props.SourceProperty
    def hostDevices(self):
        return self.source.hostDevices