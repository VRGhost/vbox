import collections

is_container = lambda el: isinstance(el, collections.Iterable) and (not isinstance(el, basestring))

class Formatter(object):
    """Object that formats input to command line arguments."""

    def __init__(self,
        all,
        mandatory,
        flags=(),
        positional=(),
        onOff=(),
    ):
        """Formatter object.
        Arguments:
            `all` - Complete list of arguments;
            `mandatory` - List of arguments that must be set;
            `flags` - arguments that are ether preset (in the form of --<flag>) or not;
            `positional` - positional arguments. Always preceed named args.
                Above field expects for the references to values to be enclosed into curly brackets ('{}')
                strings that are not enclosed into brackets will be inserted to their respective places directly;
            `onOff` - boolean arguments that have their value passes as 'on/off' string;
            `prefix` - list of strings to prepend to the output.
        """
        super(Formatter, self).__init__()

        self.all = tuple(all)
        self.flags = frozenset(flags)
        self.mandatory = frozenset(mandatory)
        self.onOff = frozenset(onOff)
        self.positional = tuple(positional)

        self._unnamed = set(self.flags)
        for el in self.positional:
            if el.startswith("{"):
                assert el.endswith("}")
                self._unnamed.add(el[1:-1])

    def __call__(self, args, kwargs):
        mapped = self._map(args, kwargs)
        self._verify(mapped)
        cast = self._castValues(mapped)
        rv = self._buildCmd(cast)
        return rv

    def _buildCmd(self, data):
        toAdd = data.copy()
        out = []
        unnamed = self._unnamed
        def _add(key, value):
            if key not in unnamed:
                out.append("--{}".format(key))
            out.append(value)

        # firstly, map positionals.
        for name in self.positional:

            if name.startswith('{'):
                assert name.endswith('}')
                key = name[1:-1]
                try:
                    _add(key, toAdd.pop(key))
                except KeyError:
                    pass
            else:
                out.append(name)
        # Now map the rest
        for (name, value) in toAdd.iteritems():
            _add(name, value)
        return tuple(out)

    def _castValues(self, data):
        """Cast argument values to their appropriate string formats."""
        flags = self.flags
        onOff = self.onOff
        cast = {}
        for (name, value) in data.iteritems():
            if name in onOff:
                newVal = "on" if value else "off"
            elif name in flags:
                newVal = ("--" + name) if value else ""
            elif is_container(value):
                newVal = ",".join(str(el) for el in value)
            else:
                newVal = str(value)

            cast[name] = newVal
        return cast

    def _verify(self, data):
        """Verify that inputs conform to the specefication."""
        provided = frozenset(data.keys())
        if not self.mandatory.issubset(provided):
            raise TypeError("Mandatory arguments {} not provided".format(self.mandatory - provided))

    def _map(self, args, kwargs):
        mapped = {}
        # Map 'args' first (if any)
        for (name, value) in zip(self.all, args):
            mapped[name] = value
        usedKeys = frozenset(mapped.keys())
        collision = usedKeys.intersection(kwargs.keys())
        if collision:
            raise TypeError("More than one value for {!r}".format(collision))
        mapped.update(kwargs)
        return mapped