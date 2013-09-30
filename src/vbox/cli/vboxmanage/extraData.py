import re

from .. import (
    base,
    util,
)

class ExtraDataOutParser(util.parsers.Dummy):

    keyRe = re.compile(r"^Key: (.*), Value: (.*)\n?$")

    def __call__(self, args, output):
        assert output.endswith('\n')
        output = output[:-1]

        key = args[-1]
        rv = None
        if key == "enumerate":
            rv = []
            keyRe = self.keyRe

            for line in output.splitlines():
                match = keyRe.match(line)
                if match:
                    data = match.groups()
                    rv.append(list(data))
                elif rv:
                    rv[-1][1] += line
                elif not line.strip():
                    continue
                else:
                    raise NotImplementedError(line)
        else:
            prefix = "Value: "
            if output.startswith(prefix):
                rv = output[len(prefix):]

        if not rv:
            raise KeyError([key, output])

        return rv

class SetExtraData(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "key", "value"),
        mandatory=("target", "key"),
        positional=("{target}", "{key}", "{value}"),
    )

class GetExtraData(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "key"),
        mandatory=("target", "key"),
        positional=("{target}", "{key}"),
    )

    parser = ExtraDataOutParser()

