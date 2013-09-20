import collections
import re

from . import (
    base,
    props,
)

STORAGE_CONTROLLER_DECLARATION_RE = re.compile("^storagecontroller([a-z]+)(\d+)$")

class Library(base.SubEntity):
    
    ide = props.SourceProperty(lambda s: tuple(el for el in s.all if el.type == "ide"))

    @props.SourceProperty
    def all(self):
        data = collections.defaultdict(dict)
        matcher = STORAGE_CONTROLLER_DECLARATION_RE

        for (key, value) in self.source.info.iteritems():
            match = matcher.match(key)
            if match:
                (param, idx) = match.groups()
                data[idx][param] = value
                continue

        print data
        1/0