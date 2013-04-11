"""Utility functions."""

import re


def iterMatches(pattern, txt):
    regex = re.compile(pattern)
    for line in txt.splitlines():
        match = regex.match(line)
        if match:
            yield match.groups()

def dequote(txt):
    quote = "\"'"
    out = txt.strip()

    if not out:
        return ""

    ch = out[0]
    if (ch in quote) and (ch == out[-1]):
        out = out[1:-1]
    return out

def splitRecord(line, sep):

    if sep not in line:
        return None

    (key, value) = line.split(sep, 1)
    return (dequote(key), dequote(value))


def iterParams(txt):
    for line in txt.splitlines():
        vals = splitRecord(line, ':')
        if vals:
            yield vals

def parseMachineReadableFmt(txt):
    for line in txt.splitlines():
        vals = splitRecord(line, '=')
        if vals:
            yield vals

def iterParamGroups(txt):
    out = {}
    for (name, value) in iterParams(txt):
        if name in out:
            yield out.copy()
            out.clear()
        out[name] = value
    if out:
        yield out

def parseParams(txt):
    """Parses parameter table."""
    return dict(iterParams(txt))

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