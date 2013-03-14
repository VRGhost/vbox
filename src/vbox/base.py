"""Base classes for logical virtualbox structure."""
import threading

from .util import boundProperty

class VirtualBoxElement(object):
    
    vb = property(lambda s: s.parent.vb)
    cli = property(lambda s: s.parent.vb.cli)
    parent = None

    def __init__(self, parent):
        super(VirtualBoxElement, self).__init__()
        self.parent = parent

class ElementGroup(VirtualBoxElement):

    _elements = None

    def __init__(self, *args, **kwargs):
        super(ElementGroup, self).__init__(*args, **kwargs)
        self._elements = self.getElements()
        for (name, value) in self._elements.iteritems():
            setattr(self, name, value)

    def getElements(self):
        raise NotImplementedError
        return {}

    def getInvalidObjects(self):
        for typ in self._elements.itervalues():
            for el in typ.getInvalidObjects():
                yield el

    def find(self, uuid):
        for typ in self._elements.itervalues():
            obj = typ.find(uuid)
            if obj is not None:
                return obj

class VirtualBoxEntityType(VirtualBoxElement):

    cls = _objIdx = _listUpToDate = _listCache = None
    _unknownObjects = None

    def __init__(self, *args, **kwargs):
        super(VirtualBoxEntityType, self).__init__(*args, **kwargs)
        self._objIdx = {}
        self._unknownObjects = []

    def create(self):
        self._listUpToDate = False

    def list(self):
        if not self._listUpToDate:
            self._listCache = tuple(self.get(id) for id in self.listRegisteredIds())

        return iter(self._listCache)

    def listRegisteredIds(self):
        raise NotImplementedError

    def get(self, objId):
        newObj = self.cls(self, objId)
        uuid = newObj.UUID
        if uuid is None:
            self._unknownObjects.append(newObj)
            rv = newObj
        elif uuid in self._objIdx:
            del newObj
            rv = self._objIdx[uuid]
        else:
            rv = newObj
            self._objIdx[uuid] = rv
        return rv

    def find(self, uuid):
        # Refresh list
        self.list()
        return self._objIdx.get(uuid)

    def getInvalidObjects(self):
        return iter(self._unknownObjects)

    def onChange(self, object):
        self._listUpToDate = False

class InfoKeeper(VirtualBoxElement):

    def __init__(self, *args, **kwargs):
        super(InfoKeeper, self).__init__(*args, **kwargs)
        self._infoUpdateLock = threading.Lock()

    _info = None
    @property
    def info(self):
        updated = self.updateInfo()
        if updated:
            self.onInfoUpdate()
        if self._info:
            rv = self._info.copy()
        else:
            rv = None
        return rv

    @info.deleter
    def info(self):
        self._info = None

    def getProp(self, name, default=None):
        if self.info:
            return self.info.get(name, default)
        else:
            return default

    def updateInfo(self, force=False):
        locked = self._infoUpdateLock.acquire(False)
        if not locked:
            # Recursive call prevention
            return False
        try:
            if (not self._info) or force:
                self._info = self._getInfo()
                return True
            return False
        finally:
            self._infoUpdateLock.release()


    def _getInfo(self):
        raise NotImplementedError

    def onInfoUpdate(self):
        pass

class VirtualBoxObject(InfoKeeper):

    idProps = ("_initId", )
    id = property(lambda s: s.getId())

    def __init__(self, parent, id):
        super(VirtualBoxObject, self).__init__(parent)
        self._initId = id

    def destroy(self):
        self.onChange()

    def onChange(self):
        self.parent.onChange(self)

    def getId(self):
        return self.iterIds().next()

    def iterIds(self):
        for name in self.idProps:
            val = getattr(self, name)
            if val:
                yield val

    def __repr__(self):
        return "<{} id={!r} uuid={!r}>".format(
            self.__class__.__name__, self._initId, self.UUID)

class VirtualBoxEntity(VirtualBoxObject):
    UUID = boundProperty(lambda s: s.getProp("UUID"))
    idProps = ("UUID", "_initId")

class VirtualBoxMedium(VirtualBoxEntity):

    def getVmAttachMedium(self):
        raise NotImplementedError

    def getVmAttachType(self):
        raise NotImplementedError
