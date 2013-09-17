class OutCheck(object):
    """Object that checks if process return code and output confirms to certain conditions."""

    okRc = ()
    extra = None

    def __init__(self, okRc, extraChecks=None):
        """Arguments:
        `okRc` - list of return codes that are assumed to be non-errorous.
        `extraChecks` - dict additional checks to be performed when `okRc` condition is satisfied.
        """
        super(OutCheck, self).__init__()
        self.okRc = frozenset(okRc)
        if extraChecks:
            self.extra = dict(extraChecks)
        else:
            self.extra = {}

    def __call__(self, args, rc, out):
        if not self.rcIsOk(rc):
            return False
        if rc in self.extra:
            func = self.extra[rc]
            if not func(args, out):
                return False
        return True

    def rcIsOk(self, rc):
        return rc in self.okRc