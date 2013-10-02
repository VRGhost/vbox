from . import base, props

class BoundNIC(base.SubEntity):
    """NIC bound to the VM."""

    type = props.StrOrNone(**props.modifySelfRef("nic{self.idx}"))
    cableConnected = props.OnOff(**props.modifySelfRef("cableconnected{self.idx}"))
    hw = props.Str(**props.modifySelfRef("nictype{self.idx}"))
    internalNetwork = props.Str(**props.modifySelfRef("intnet{self.idx}"))
    mac = props.Str(**props.modifySelfRef("macaddress{self.idx}"))

    def type():
        def fget(self):
            typ = self.source.info["nic{}".format(self.idx)]
            if typ == "none":
                rv = None
            else:
                rv = typ
            return typ
        def fset(self, value):
            prev = self.type

            if not value:
                rv = "none"
            else:
                available = self.listAvailable(value)
                kw = {"nic{}".format(self.idx): value}
                if available:
                    # Set try to bind adapter simultaniously with the adapter type
                    kw[self._getAdapterPropName(value)] = available[0]

                if not prev:
                    # If this adapter is being created from nothing, ensure that cable is connected by default.
                    kw["cableconnected{}".format(self.idx)] = "on"

                self.source.modify(**kw)
                rv = value
            return rv
        return locals()
    type = props.SourceProperty(**type())

    def mac():
        """Hardware MAC address."""
        def fget(self):
            key = "macaddress{}".format(self.idx)
            rv = self.source.info.get(key)
            if rv:
                rv = rv.lower()
                if ':' not in rv:
                    old = rv
                    parts = []
                    while old:
                        parts.append(old[:2])
                        old = old[2:]
                rv = ':'.join(parts)
            return rv
        def fset(self, value):
            if value and ':' in value:
                value = value.replace(':', '')
            key = "macaddress{}".format(self.idx)
            self.source.modify(**{key: value})
        return locals()
    mac = property(**mac())

    def hostAdapter():
        """In case when chosen nic type requires a host-side adapter, this property
        provides access to getting/setting it.
        """
        def fget(self):
            name = self._getAdapterPropName()
            if name:
                rv = self.source.info[name]
            else:
                rv = None
            return rv

        def fset(self, value):
            if value not in self.listAvailable():
                raise ValueError("{!r} is not in {!r}".format(value, self.listAvailable()))
            self.source.modify(**{self._getAdapterPropName(): value})
        return locals()
    hostAdapter = props.SourceProperty(**hostAdapter())

    def listAvailable(self, type=None):
        if not type:
            type = self.type

        if type == "hostonly":
            rv = [el["Name"] for el in self.interface.networking.hostOnlyInterfaces]
        elif type == "bridged":
            rv = [el["Name"] for el in self.interface.networking.bridgedInterfaces]
        else:
            rv = ()
        return tuple(rv)

    def _getAdapterPropName(self, type=None):
        if not type:
            type = self.type

        if type == "hostonly":
            key = "hostonlyadapter{}"
        elif type == "bridged":
            key = "bridgedadapter{}"
        else:
            return None

        return key.format(self.idx)

    def __init__(self, parent, idx):
        super(BoundNIC, self).__init__(parent)
        self.idx = idx

    def __repr__(self):
        return "<{}#{} for {!r}>".format(self.__class__.__name__, self.idx, self.parent)


class Library(base.Library):

    @props.SourceProperty
    def hostOnlyInterfaces(self):
        return self.source.hostOnlyInterfaces

    @props.SourceProperty
    def bridgedInterfaces(self):
        return self.source.bridgedInterfaces