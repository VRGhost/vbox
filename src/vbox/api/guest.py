import collections
import os
import re

from . import (
    base,
    props,
)

class GuestControl(object):

    def __init__(self, source, login, password):
        super(GuestControl, self).__init__()
        self.source = source
        self.login = login
        self.password = password

    def copyTo(self, srcFile, outFile):
        assert os.path.isfile(srcFile)
        self.source.guest.control.copyTo(
            dest=outFile, src=srcFile,
            user=self.login, password=self.password
        )

    def __exit__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

class GuestAdditions(base.SourceObjectProxy):

    @props.SourceProperty
    def info(self):
        return self.source.guest.properties.all()

    @props.SourceProperty
    def net(self):
        netRe = re.compile(r"^/VirtualBox/GuestInfo/Net/(\d+)/(.*)$")
        data = collections.defaultdict(dict)

        for el in self.info:
            match = netRe.match(el["name"])
            if match:
                (idx, path) = match.groups()
                path = path.split('/')
                target = data[int(idx)]

                infix = path[:-1]
                while infix:
                    key = infix.pop(0)
                    target.setdefault(key, {})
                    target = target[key]

                target[path[-1]] = el["value"]

        keys = sorted(data.keys())
        rv = tuple(data[key] for key in keys)
        return rv

    def control(self, login, password):
        """Bound guest control object."""
        return GuestControl(self.source, login, password)