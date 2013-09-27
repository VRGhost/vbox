"""Utility functions."""
import re

class MappingList(object):

    def __init__(self):
        super(MappingList, self).__init__()
        self._pairs = []
        self._index = {}
        self._multiple = set()

    def append(self, key, value):
        self._pairs.append((key, value))
        _index = self._index
        if key in _index:
            self._multiple.add(key)
            _index.pop(key)
        else:
            _index[key] = (len(self._pairs)-1, value)

    def __getitem__(self, key):
        try:
            return self._index[key][1]
        except KeyError:
            if key in self._multiple:
                raise IndexError("Multiple values for {!r}".format(key))
            else:
                raise KeyError(key)

    def __contains__(self, key):
        return (key in self._index) or (key in self._multiple)

    def __len__(self):
        return len(self._pairs)

    def get(self, key, default=None):
        try:
            rv = self._index.get(key, default)
        except KeyError:
            if key in self._multiple:
                raise IndexError("Multiple values for {!r}".format(key))
            else:
                raise KeyError(key)
        if rv is default:
            return rv
        else:
            return rv[1]

    def index(self, key):
        rv = self._index.get(key)
        if rv is not None:
            return rv[0]
        else:
            for (idx, (pairKey, value)) in enumerate(self._pairs):
                if pairKey == key:
                    return idx

        raise ValueError("{!r} is not in {}".format(key, self.__class__.__name__))

    def getByIndex(self, idx):
        return self._pairs[idx]

    def iteritems(self):
        return iter(self._pairs)

    def items(self):
        return tuple(self.iteritems())

    def iterkeys(self):
        return self._index.iterkeys()

    def keys(self):
        return tuple(self.iterkeys())

class Dummy(object):
    """Base dummy parser.

        Always returns input that was provided.
    """

    def __call__(self, args, output):
        return output

class Conditional(Dummy):
    """Conditional parser that calls subparsers depending on matching filter."""

    def __init__(self, children):
        super(Conditional, self).__init__()
        self.children = tuple(children)

    def __call__(self, args, output):
        for (check, sub) in self.children:
            if check(args, output):
                return sub(args, output)
        else:
            raise KeyError("Unable to match {!r}:{!r}".format(args, output))

class Strings(Dummy):
    """Parses collection of strings."""

    def __call__(self, args, output):
        dequote = self.dequote
        return tuple(dequote(el) for el in output.splitlines())

    def dequote(self, txt):
        quote = "\"'"
        out = txt.strip()

        if not out:
            return ""

        ch = out[0]
        if (ch in quote) and (ch == out[-1]):
            out = out[1:-1]
        return out

class Items(Strings):
    """Parser for (name: value) type of output."""
    sep = ':'

    def __call__(self, args, output):
        return tuple(self._parseItems(output))

    def _parseItems(self, output):
        sep = self.sep
        dequote = self.dequote

        for line in output.splitlines():
            if sep not in line:
                continue
            (key, value) = line.strip().split(sep, 1)
            yield (dequote(key), dequote(value))


class Dicts(Items):
    """to Multiple dicts."""

    def __call__(self, args, output):
        return tuple(self._parseDicts(output))

    def _parseDicts(self, output):
        out = MappingList()
        for (key, value) in self._parseItems(output):
            if key in out:
                yield out
                out = MappingList()
            out.append(key, value)
        if out:
            yield out

class Dict(Items):
    """To one dict."""

    def __call__(self, args, output):
        return self._toDict(output)

    def _toDict(self, output):
        out = MappingList()
        for (key, value) in self._parseItems(output):
            out.append(key, value)
        return out