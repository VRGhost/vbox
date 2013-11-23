import re

from . import (
    base,
    props,
    exceptions,
)

class SharedFolder(base.SubEntity):

    removed = False

    def __init__(self, parent, idx, mode):
        super(SharedFolder, self).__init__(parent)
        self.mode = mode.lower()
        self.idx = idx

    @props.SourceProperty
    def name(self):
        if self.removed:
            raise Exception("This folder had been removed")

        fldName = "SharedFolderName{}Mapping{}".format(self.mode.title(), self.idx)
        return self.source.info[fldName]

    @props.SourceProperty
    def path(self):
        if self.removed:
            raise Exception("This folder had been removed.")

        fldName = "SharedFolderPath{}Mapping{}".format(self.mode.title(), self.idx)
        return self.source.info[fldName]

    @props.SourceProperty
    def permanent(self):
        return "transient" in self.mode

    def remove(self):
        self.source.sharedFolder(action="remove", name=self.name)
        self.removed = True

class SharedFolderAccessor(base.SubEntity):

    def set(self, name, path):
        try:
            old = self.get(name)
        except KeyError:
            pass
        else:
            old.remove()

        self.source.sharedFolder(action="add", name=name, hostpath=path)
        return self.get(name)

    def get(self, name):
        for folder in self.listRegistered():
            if folder.name == name:
                return folder
        raise KeyError(name)

    def listRegistered(self):
        matcher = re.compile("SharedFolderName(Transient|Machine)Mapping(\d+)")
        out = []
        for name in self.source.info.iterkeys():
            match = matcher.match(name)
            if match:
                folder = SharedFolder(self, match.group(2), match.group(1))
                out.append(folder)
        return tuple(out)