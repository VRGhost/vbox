import datetime
import os
import re
import tempfile
import collections

from . import base

class OS(base.DeverativeInfo):
    """Opbject that provides information and os.path library appropriate for current guest."""

    name = property(lambda s: s.info["Product"].lower())
    version = property(lambda s: s.info["Version"])
    release = property(lambda s: s.info["Release"])
    loggedInUsers = property(lambda s: s.info["LoggedInUsersList"])

    def _getInfo(self):
        src = self.parent.info or {}
        prefix = r"/VirtualBox/GuestInfo/OS/"
        cutLen = len(prefix)

        out = {
            "Product": "",
            "LoggedInUsersList": "",
            "Version": "",
            "Release": "",
        }
        data = dict((key[cutLen:], val["value"])
            for (key, val) in src.iteritems()
            if key.startswith(prefix)
        )
        out.update(data)
        out["LoggedInUsersList"] = out["LoggedInUsersList"].split(",")
        return out

    @property
    def path(self):
        """Select appropriate os.path module."""
        name = self.name
        if name == "linux":
            import posixpath as out
        elif name == "windows":
            import ntpath as out
        else:
            raise Exception("Unexpected guest name {!r}".format(name))
        return out

class Net(base.DeverativeInfo):

    def _getInfo(self):
        src = self.parent.info or {}
        prefix = r"/VirtualBox/GuestInfo/Net/"
        cutLen = len(prefix)

        out = collections.defaultdict(dict)
        for value in src.itervalues():
            if not value["name"].startswith(prefix):
                continue

            propName = value["path"][-1]
            val = value["value"]

            if value["path"][3].isdigit():
                hwId = int(value["path"][3])
                out[hwId][propName] = val
            else:
                assert propName == "Count", value
                pass

        return out
            

    def __getitem__(self, key):
        return self.info[key]

    def __iter__(self):
        return self.info.itervalues()

    def __len__(self):
        return len(self.info)

class Info(base.VmElement):

    os = net = None

    def __init__(self, parent):
        super(Info, self).__init__(parent)
        self.os = OS(self)
        self.net = Net(self)
    
    def _getInfo(self):
        reFields = ("name", "value", "timestamp", "flags")
        lineRe = ", ".join("{0}:\s*(?P<{0}>.*)".format(fld) for fld in reFields)
        lineRe = re.compile("^{}$".format(lineRe), re.I)
        def parse_line(txt):
            match = lineRe.match(txt)
            assert match
            out = match.groupdict()
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