"""Base classes for logical virtualbox structure."""

class VirtualBoxElement(object):
    
    def __init__(self, vb):
        super(VirtualBoxElement, self).__init__()
        self.vb = vb

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
        newObj = self.cls(self, self.vb, objId)
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
        return self._objIdx.get(uuid)

    def getInvalidObjects(self):
        return iter(self._unknownObjects)

    def onDestroy(self, object):
        self._listUpToDate = False


class VirtualBoxEntity(VirtualBoxElement):

    idProps = ("UUID", "_initId")

    def __init__(self, parent, vb, id):
        super(VirtualBoxEntity, self).__init__(vb)
        self._initId = id
        self.parent = parent

    def getProp(self, name, default=None):
        if self.info:
            return self.info.get(name, default)
        else:
            return default

    _info = None
    @property
    def info(self):
        if not self._info:
            self._info = self._getInfo()
            self.onInfoUpdate()
        if self._info:
            rv = self._info.copy()
        else:
            rv = None
        return rv

    @info.deleter
    def info(self):
        self._info = None

    _uuidCache = None
    @property
    def UUID(self):
        """UUID property with no option of un-caching UUID."""
        if self._uuidCache is None:
            self._uuidCache = self.getProp("UUID")
        return self._uuidCache

    def _getInfo(self):
        raise NotImplementedError

    def destroy(self):
        self.parent.onDestroy(self)

    def getId(self):
        for name in self.idProps:
            val = getattr(self, name)
            if val:
                return val

    def onInfoUpdate(self):
        pass

    def __repr__(self):
        return "<{} id={!r} uuid={!r}>".format(self.__class__.__name__, self._initId, self.UUID)

class VirtualBoxMedium(VirtualBoxEntity):

    def getVmAttachMedium(self):
        raise NotImplementedError

    def getVmAttachType(self):
        raise NotImplementedError
