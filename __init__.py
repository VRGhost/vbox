# This file makes pyvb's reposetory a proper Python package.
#
# So one can add projects' repo as submodule tho its parent project.

import imp
import os

MODULE_NAME = "vbox"
THIS_DIR = os.path.realpath(os.path.dirname(__file__))

vbox_module = imp.find_module(MODULE_NAME, [os.path.join(THIS_DIR, "src",)])
assert vbox_module
imp.load_module(MODULE_NAME, *vbox_module)

from vbox import *