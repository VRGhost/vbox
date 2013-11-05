import itertools

from . import base

#  {"IO": "0x3F8", "IRQ": 4, "type": "server", "name": "source_{}_com_1".format(self.name)}, # COM1
class SerialPortRecord(base.SubConfigEntity):

    setAttrs = ("type", "IO", "IRQ", )
    customHandlers = ("target", )

    def setup_target(self, obj, config):
        obj.target = config

    def ensure_target(self, obj, config):
        curTarget = obj.target
        if curTarget not in (config, "\\\\.\\pipe\\" + config):
            raise self.exceptions.EnsureMismatch(obj, "target", config, curTarget)

class Serial(base.SubConfigEntity):

    customHandlers = ("targets", )

    def setup_targets(self, vm, data):
        for (serial, config) in itertools.izip_longest(vm.serial, data):
            if not serial:
                raise self.exceptions.ConfigMismatch("No nic slot for data {!r}".format(config))
            self._setupSerial(serial, config)

    def ensure_targets(self, vm, data):
        for (serial, config) in itertools.izip_longest(vm.serial, data):
            if not serial:
                raise self.exceptions.ConfigMismatch("No nic slot for data {!r}".format(config))

            if config:
                cfgObj = SerialPortRecord(self)
                cfgObj.ensure(serial, config)
            else:
                if serial.type != None:
                    raise self.exceptions.EnsureMismatch(serial, "type", None, serial.type)


    def _setupSerial(self, vmSerial, config):
        if not config:
            vmSerial.type = None
            return

        cfgObj = SerialPortRecord(self)
        cfgObj.setup(vmSerial, config)