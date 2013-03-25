import re

from .subCmd import ArgCmd

class GetExtraData(ArgCmd):
    changesVmState = False
    nargs = 1
    opts = ("name", )

    _valueRe = re.compile("^Value:\s*(.*)$", re.I)
    _keyValueRe = re.compile("^Key:\s*(.*),\s*Value:\s*(.*)$", re.I)

    def dictToCmdLine(self, kwargs):
        name = kwargs.get("name")
        if not name:
            name = "enumerate"
        return [name]

    def getRcHandlers(self):
        return {
            0: self._parseOutput,
        }

    def _parseOutput(self, cmd, output):
        if "enumerate" in cmd:
            rv = {}
            splitRe = self._keyValueRe

            key = None
            for line in output.splitlines():
                match = splitRe.match(line)
                if match:
                    key = match.group(1).strip()
                    rv[key] = match.group(2).strip()
                else:
                    assert key
                    # Append text to previous key
                    rv[key] += '\n' + line.strip()
        else:
            match = self._valueRe.match(output)
            assert match
            rv = match.group(1).strip()
        return rv

class SetExtraData(ArgCmd):
    changesVmState = False
    nargs = 3