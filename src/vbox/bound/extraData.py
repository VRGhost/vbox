from . import base

_NULL_ = object()

class ExtraData(base.CliAccessor):
    """Extra data accessor."""

    def __init__(self, cli, id):
        super(ExtraData, self).__init__(cli)
        self.id = id

    def items(self):
        return tuple(self.iteritems())

    def iteritems(self):
        for key in self.keys():
            yield (key, self.get(key))

    @base.refreshed
    def keys(self):
        out = []
        for key in self.possibleKeys:
            try:
                self.get(key)
            except KeyError:
                continue
            else:
                out.append(key)
        return frozenset(out)

    @base.refreshed
    def get(self, key, default=_NULL_):
        try:
            return self.cli.manage.getExtraData(self.id, key)
        except KeyError:
            if default is _NULL_:
                raise
            else:
                return default

    @base.refreshedProperty
    def possibleKeys(self):
        return frozenset(el[0] for el in self.cli.manage.getExtraData(self.id, "enumerate"))

    @base.refreshing
    def rm(self, key):
        self.cli.manage.setExtraData(self.id, key)

    @base.refreshing
    def set(self, key, value):
        self.cli.manage.setExtraData(self.id, key, value)