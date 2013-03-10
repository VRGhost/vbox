"""Base classes for logical virtualbox structure."""

class ElementGroup(object):

    _elements = None

    def __init__(self):
        super(ElementGroup, self).__init__()
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
        # Refresh list
        self.list()
        return self._objIdx.get(uuid)

    def getInvalidObjects(self):
        return iter(self._unknownObjects)

    def onChange(self, object):
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
        self.onChange()

    def onChange(self):
        self.parent.onChange(self)

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
