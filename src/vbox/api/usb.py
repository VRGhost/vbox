import re
import vbox.base

from . import (
    base,
    props,
    exceptions,
)

class HostDevice(base.SubEntity):

    state = property(lambda s: s.getPayload()["Current State"].lower())
    product = property(lambda s: s.getPayload()["Product"])
    manufacturer = property(lambda s: s.getPayload()["Manufacturer"])
    productId = property(lambda s: int(s.getPayload()["ProductId"].split()[0], 16))
    vendorId = property(lambda s: int(s.getPayload()["VendorId"].split()[0], 16))

    def __init__(self, parent, uuid):
        super(HostDevice, self).__init__(parent)
        self.UUID = uuid

        def _getPayload():
            for rec in self.source.getHostDevices():
                if rec["UUID"] == self.UUID:
                    return dict(rec)
            raise KeyError(self.UUID)

        self.getPayload = base.ProxyRefreshTrail(
            _getPayload, depends=(self.source.getHostDevices, )
        )

    def __repr__(self):
        try:
            payload = self.getPayload()
        except KeyError:
            payload = None

        return "<{} payload={}>".format(self.__class__.__name__, payload)

class VmDevice(base.SubEntity):

    UUID = property(lambda s: s.source.info["USBAttachedUUID" + s.idx])
    vendorId = property(lambda s: int(s.source.info["USBAttachedVendorId" + s.idx], 16))
    productId = property(lambda s: int(s.source.info["USBAttachedProductId" + s.idx], 16))
    revisionId = property(lambda s: int(s.source.info["USBAttachedRevision" + s.idx], 16))
    manufacturer = property(lambda s: s.source.info["USBAttachedManufacturer" + s.idx])
    product = property(lambda s: s.source.info["USBAttachedProduct" + s.idx])
    address = property(lambda s: s.source.info["USBAttachedAddress" + s.idx])
    state = property(lambda s: "attached")

    def __init__(self, parent, idx):
        super(VmDevice, self).__init__(parent)
        self.idx = idx

class VmUsb(base.SubEntity):

    enabled = props.OnOff(**props.modify("usb"))
    ehci = props.OnOff(**props.modify("usbehci")) # Enables/disable usb 2.0

    def attach(self, device):
        if device.state == "attached":
            raise Exception("This USB device is already attached.")

        target = device.UUID
        self.source.usbAttach(target)
        # notify the device backend that it should be refreshed.
        device.source.clearCache()
        for el in self.devices:
            if el.UUID == target:
                return el
        else:
            raise Exception("Device {!r} that was previously attached is now lost.".format(target))

    @props.SourceProperty
    def devices(self):
        matcher = re.compile(r"^USBAttachedUUID(\d+)$")
        foundIds = []
        for key in self.source.info.iterkeys():
            match = matcher.match(key)
            if match:
                foundIds.append(match.group(1))
        return [
            VmDevice(self, uuid)
            for uuid in foundIds
        ]


class Library(base.Library):

    @props.SourceProperty
    def hostDevices(self):
        return [
            HostDevice(self, rec["UUID"])
            for rec in self.source.getHostDevices()
        ]