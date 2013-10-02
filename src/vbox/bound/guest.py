from . import base

class GuestEl(base.CliAccessor):

    def __init__(self, vm):
        super(GuestEl, self).__init__(vm.cli)
        self.vm = vm
        self.id = vm.id
        self.vm.addCacheClearCallback(self._onVmRefresh)

    def _onVmRefresh(self, vm):
        assert vm is self.vm
        self.clearCache()

class GuestProperties(GuestEl):

    @base.refreshed
    def all(self):
        return self.cli.manage.guestProperty.enumerate(self.id)

class GuestControl(GuestEl):

    def copyTo(self, src, dest, user, password="", dryrun=False, followSymlinks=True, recursive=False):
        return self.cli.manage.guestControl.copyTo(
            self.id, src, dest,
            username=user, password=password,
            dryrun=dryrun, follow=followSymlinks,
            recursive=recursive,
        )

    def execute(self, program, user, password="", environment=None, timeout=None, arguments=None,
        waitExit=None, waitStdout=None, waitStderr=None
    ):
        """
            http://www.virtualbox.org/manual/ch08.html#vboxmanage-guestcontrol

            Timeout in seconds.
        """
        kw = {
            "target": self.id,
            "image": str(program),
            "username": user,
            "password": password,
        }
        if environment:
            parts = []
            do_quote = lambda what: "'{}'".format(str(what)) if ' ' in what else str(what)

            for (name, value) in environment.iteritems():
                val = "{}=".format(do_quote(name))
                if value is not None:
                    val += do_quote(value)
                parts.append(val)
            kw["environment"] = ' '.join(parts)

        if timeout:
            kw["timeout"] = int(round(timeout * 1000))

        if arguments:
            kw["arguments"] = tuple(arguments)

        if waitExit is not None:
            kw["waitExit"] = waitExit

        if waitStdout is not None:
            kw["waitStdout"] = waitStdout

        if waitStderr is not None:
            kw["waitStderr"] = waitStderr

        return self.cli.manage.guestControl.execute(**kw)

    def stat(self, paths, user, password):
        paths = tuple(paths)
        assert paths, "Non-empty list of paths to be checked returned."

        out = self.cli.manage.guestControl.stat(
            self.id, files=paths, username=user, password=password,
        )
        assert frozenset(out.keys()).issubset(paths), (out.keys(), paths)
        for fname in paths:
            if fname not in out:
                out[fname] = None # File does not exist
        return out

class Guest(object):

    def __init__(self, vm):
        self.properties = GuestProperties(vm)
        self.control = GuestControl(vm)