import os
import sys

from . import (
    base,
    props,
)

_NOT_SET_ = object()

class Serial(base.SubEntity):

    def IRQ():
        def fget(self):
            if self.mainValue:
                return self.mainValue[1]
            else:
                return None
        def fset(self, value):
            self.mainValue = self._computeMainValue(irq=value)
        return locals()
    IRQ = props.SourceProperty(**IRQ())

    def IO():
        def fget(self):
            if self.mainValue:
                return self.mainValue[0]
            else:
                return None
        def fset(self, value):
            self.mainValue = self._computeMainValue(io=value)
        return locals()
    IO = props.SourceProperty(**IO())

    def type():
        doc = "The type property."
        def fget(self):
            if self.mode:
                if len(self.mode) == 2:
                    rv = self.mode[0]
                    assert rv in ("server", "client")
                else:
                    rv = "device"
            else:
                rv = None
            return rv
        def fset(self, value):
            self.mode = self._computeMode(type=value)
        return locals()
    type = props.SourceProperty(**type())

    def target():
        doc = "The target property."
        def fget(self):
            if self.mode:
                return self.mode[-1]
            else:
                return None
        def fset(self, value):
            self.mode = self._computeMode(target=value)
        return locals()
    target = props.SourceProperty(**target())

    def mainValue():
        def fget(self):
            name = "uart{}".format(self.idx)
            txt = self.source.info.get(name)
            if txt in (None, "off"):
                rv = None
            else:
                assert ',' in txt, txt
                (io, irq) = txt.split(',')
                rv = (
                    int(io, 16),
                    int(irq),
                )
            return rv
        def fset(self, value):
            name = "uart{}".format(self.idx)
            if value:
                assert len(value) == 2
                vmVal = [
                    "0x{:X}".format(value[0]), # io
                    str(value[1]), # irq
                ]
            else:
                vmVal = "off"
            self.source.modify(**{name: vmVal})
        return locals()
    mainValue = props.SourceProperty(**mainValue())

    def mode():
        doc = "The `uartmode` property."
        def fget(self):
            name = "uartmode{}".format(self.idx)
            txt = self.source.info.get(name)
            if txt in (None, "disconnected"):
                rv = None
            else:
                rv = txt.split(',')
                assert len(rv) <= 2
            return rv
        def fset(self, value):
            name = "uartmode{}".format(self.idx)
            if not value:
                mode = "disconnected"
            else:
                assert len(value) == 2
                if value[0] == "device":
                    mode = value[1]
                elif value[0] in ("client", "server") and sys.platform == "win32":
                    winPipePrefix = "\\\\.\\pipe\\"
                    if not value[1].startswith(winPipePrefix):
                        value = (value[0], winPipePrefix + value[1])
            self.source.modify(**{name: value})
        return locals()
    mode = props.SourceProperty(**mode())

    def _computeMode(self, type=_NOT_SET_, target=_NOT_SET_):
        if None in (type, target):
            rv = None
        elif type is _NOT_SET_:
            assert target is not _NOT_SET_
            if self.type:
                type = self.type
            else:
                type = "server"
            rv = (type, target)
        elif target is _NOT_SET_:
            assert type is not _NOT_SET_
            if self.target:
                target = self.target
            elif type == "device":
                if sys.platform == "win32":
                    target = "COM1"
                else:
                    target = "/dev/ttyS0"
            elif type in ("client", "server"):
                target = "unnamed_vbox_pipe"
            else:
                raise NotImplementedError(type)
            rv = (type, target)
        else:
            assert _NOT_SET_ not in (type, target)
            rv = (type, target)
        return rv

    def _computeMainValue(self, io=_NOT_SET_, irq=_NOT_SET_):
        if None in (io, irq):
            rv = None
        elif io is _NOT_SET_:
            assert irq is not _NOT_SET_
            if self.IO is not None:
                io = self.IO
            else:
                # Try guessing IO from the set of traditional values
                if irq == 4:
                    io = 0x3F8  # = COM1
                else:
                    io = 0x2f8 # = COM2 if irq == 3
            rv = (io, irq)
        elif irq is _NOT_SET_:
            assert io is not _NOT_SET_
            if self.IRQ is not None:
                irq = self.IRQ
            else:
                if io == 0x3F8:
                    irq = 4     # COM1
                elif io == 0x2F8:
                    irq = 3     # COM2
                elif io == 0x3E8:
                    irq = 4     # COM3
                else:
                    irq = 3     # COM4 if io == 0x2E8
            rv = (io, irq)
        else:
            assert _NOT_SET_ not in (io, irq)
            rv = (io, irq)
        return rv

    def __init__(self, parent, idx):
        super(Serial, self).__init__(parent)
        self.idx = idx