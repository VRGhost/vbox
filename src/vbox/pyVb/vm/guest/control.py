import datetime
import tempfile
import os

from . import base

class Control(base.VmElement):

    def __init__(self, vm, user, password):
        super(Control, self).__init__(vm)
        self.user = user
        self.password = password

    def copyTo(self, src, dst, follow=True, recursive=True):
        assert os.path.exists(src), src
        src = os.path.abspath(src)
        print self.cli.manage.guestcontrol.copyto(
            self.vm.getId(), src, dst, 
            username=self.user, password=self.password,
            follow=follow, recursive=recursive
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

class ControlUserWrapper(object):
    """Guest control requires guest user credentials.

    This object should offer more convenient way of storing or providing this information.
    """

    def __init__(self, vm):
        self.vm = vm

    def auth(self, user, password=""):
        return Control(self.vm, user, password)

    def __call__(self, *args, **kwargs):
        return self.auth(*args, **kwargs)