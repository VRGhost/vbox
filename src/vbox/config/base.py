import logging

from . import exceptions

log = logging.getLogger(__name__)

class ConfigEntity(object):

    exceptions = exceptions
    setAttrs = () # List of attribute names to be set via 'setattr'
    ignoreKeys = () # List of config keys to be ignored
    subConfigs = None
    customHandlers = () # List of keys that are managed by custom handlers in `self`
    # Handler have to be named "setup_{name}" and "ensure_{name}" respectivly

    def __init__(self, interface):
        super(ConfigEntity, self).__init__()
        self.interface = interface
        self.api = interface.api
        self.setAttrs = frozenset(self.setAttrs)
        self.ignoreKeys = frozenset(self.ignoreKeys)
        self.customHandlers = frozenset(self.customHandlers)
        self.subConfigs = dict((key, cls(self))
            for (key, cls)
            in (self.subConfigs or {}).iteritems()
        )

    def fromDict(self, data):
        """Create controlled entity object using definitions provided by the dictionary.

        This is two-faced function - in case if the object did not exist, it has to create it and
        set up its properties accordingly.

        If it exists - it has to verify that all objects' properties match the definitions
        and raise exceptions.ConfigMismatch exception
        """
        raise NotImplementedError

    def ensure(self, obj, data):
        remainingAttrs = set(data.keys()) - self.ignoreKeys

        for name in self.setAttrs:
            try:
                reqValue = data[name]
            except KeyError:
                continue
            remainingAttrs.remove(name)

            realValue = getattr(obj, name)
            if realValue != reqValue:
                raise self.exceptions.EnsureMismatch(obj, name, reqValue, realValue)

        for (name, sub) in self.subConfigs.iteritems():
            try:
                value = data[name]
            except KeyError:
                continue
            sub.ensure(obj, data[name])
            remainingAttrs.remove(name)

        for name in self.customHandlers:
            try:
                value = data[name]
            except KeyError:
                continue
            handler = getattr(self, "ensure_{}".format(name))
            handler(obj, value)
            remainingAttrs.remove(name)

        if remainingAttrs:
            raise self.exceptions.ConfigError(remainingAttrs)

    def setup(self, obj, data):
        remainingAttrs = set(data.keys()) - self.ignoreKeys
        for name in self.setAttrs:
            try:
                value = data[name]
            except KeyError:
                continue
            if not hasattr(obj, name):
                raise AttributeError("Object {!r} does not have attribute {!r}".format(obj, name))
            try:
                setattr(obj, name, value)
            except AttributeError:
                log.exception("Unable to assign value {!r} to {!r}.{!r}".format(value, obj, name))
                raise AttributeError("Unable to set attribute {!r}.{!r}".format(obj, name))
            remainingAttrs.remove(name)

        for (name, sub) in self.subConfigs.iteritems():
            try:
                value = data[name]
            except KeyError:
                continue
            sub.setup(obj, data[name])
            remainingAttrs.remove(name)

        for name in self.customHandlers:
            try:
                value = data[name]
            except KeyError:
                continue
            handler = getattr(self, "setup_{}".format(name))
            handler(obj, value)
            remainingAttrs.remove(name)

        if remainingAttrs:
            raise self.exceptions.ConfigError(remainingAttrs)

class SubConfigEntity(ConfigEntity):

    def __init__(self, parent):
        super(SubConfigEntity, self).__init__(parent.interface)
        self.parent = parent

    def setup(self, obj, data):
        myObj = self.parentObjToMyObj(obj)
        return super(SubConfigEntity, self).setup(myObj, data)

    def ensure(self, obj, data):
        myObj = self.parentObjToMyObj(obj)
        return super(SubConfigEntity, self).ensure(myObj, data)

    def parentObjToMyObj(self, parentObj):
        """Map parent object to the object controlled by this entity."""
        return parentObj