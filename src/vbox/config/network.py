import itertools

from . import base

class NIC(base.SubConfigEntity):

    setAttrs = ("type", "cableConnected", "hw", "hostAdapter")

class Network(base.SubConfigEntity):

    customHandlers = ("targets", )

    def setup_targets(self, vm, data):
        for (nic, config) in itertools.izip_longest(vm.nics, data):
            if not nic:
                raise self.exceptions.ConfigMismatch("No nic slot for data {!r}".format(config))
            self._setupNic(nic, config)

    def ensure_targets(self, vm, data):
        for (nic, config) in itertools.izip_longest(vm.nics, data):
            if not nic:
                raise self.exceptions.ConfigMismatch("No nic slot for data {!r}".format(config))

            if config:
                cfgObj = NIC(self)
                cfgObj.ensure(nic, config)
            else:
                if nic.type != None:
                    raise self.exceptions.EnsureMismatch(nic, "type", None, nic.type)

    def _setupNic(self, nic, config):
        if not config:
            nic.type = None
            return

        cfgObj = NIC(self)
        cfgObj.setup(nic, config)