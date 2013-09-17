"""Utility functions."""

import re

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
        out = {}
        for (key, value) in self._parseItems(output):
            if key in out:
                yield out
                out = {}
            out[key] = value
        if out:
            yield out

class Dict(Items):
    """To one dict."""

    def __call__(self, args, output):
        return self._toDict(output)

    def _toDict(self, output):
        out = {}
        for (key, value) in self._parseItems(output):
            if key in out:
                raise Exception("Duplicate value for {!r} in {!r}".format(key, output))
            out[key] = value
        return out


# def iterMatches(pattern, txt):
#     regex = re.compile(pattern)
#     for line in txt.splitlines():
#         match = regex.match(line)
#         if match:
#             yield match.groups()

# def iterParams(txt):
#     for line in txt.splitlines():
#         vals = splitRecord(line, ':')
#         if vals:
#             yield vals

# def parseMachineReadableFmt(txt):
#     for line in txt.splitlines():
#         vals = splitRecord(line, '=')
#         if vals:
#             yield vals


def toMBytes(label):
    if label is None:
        return None
    (num, typ) = label.split()
    typ = typ.lower()
    num = int(num)
    if typ == "mbytes":
        rv = num
    else:
        raise Exception("Unable to parse label {!r}".format(label))
    return rv