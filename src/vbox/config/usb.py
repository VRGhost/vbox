from . import base

class Usb(base.SubConfigEntity):

    customHandlers = ("enabled", )

    def setup_enabled(self, vm, data):
        vm.usb.enabled = data

    def ensure_enabled(self, vm, data):
        if vm.usb.enabled != data:
            raise self.exceptions.ConfigMismatch("VM usb enabled is set to {!r} while {!r} expected".format(
                    vm.usb.enabled, data
                ))