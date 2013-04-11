import datetime
import tempfile
import os

from . import base

class Info(base.VmElement):
    
    def _getInfo(self):
        def parse_line(txt):
            parts = txt.split(",", 3)
            assert len(parts) == 4, (parts, txt)
            out = {}
            for el in parts:
                (name, value) = el.split(":", 1)
                out[name.strip().lower()] = value.strip()

            flags = [el.strip() for el in out["flags"].split(",")]
            out["flags"] = [el for el in flags if el]
            timestamp = int(out["timestamp"])
            timestamp = timestamp / (10.0 ** 9)
            timestamp = datetime.datetime.fromtimestamp(timestamp)
            out["timestamp"] = timestamp
            out["path"] = tuple(el for el in out["name"].split('/') if el)
            return out

        out = {}
        info = self.cli.manage.guestproperty.enumerate(self.vm.getId())
        for line in info.splitlines():
            line = line.strip()
            data = parse_line(line)
            out[data["name"]] = data
        return out

    def ip(self):
        """Yields (network_adapter_id, ip) tuples."""
        info = self.info or {}
        for data in info.itervalues():
            if ("Net" in data["path"]) and ("IP" in data["path"]):
                yield (int(data["path"][3]), data["value"])

class Control(base.VmElement):

    def copyTo(self, src, dst, user=None, password=None, follow=True, recursive=True):
        assert os.path.exists(src), src
        src = os.path.abspath(src)
        self.cli.guestcontrol.copyto(src, dst, follow=follow, recursive=recursive)

class Guest(base.VmElement):

    info = control = None

    def __init__(self, *args, **kwargs):
        super(Guest, self).__init__(*args, **kwargs)
        self.info = Info(self.vm)
        self.control = Control(self.vm)