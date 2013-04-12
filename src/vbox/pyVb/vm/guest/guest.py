import datetime
import tempfile
import os

from . import base, info, control

class Guest(base.VmElement):

    info = control = None

    def __init__(self, *args, **kwargs):
        super(Guest, self).__init__(*args, **kwargs)
        self.info = info.Info(self)
        self.control = control.ControlUserWrapper(self)