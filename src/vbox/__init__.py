"""VBox project uses layered architecture

'VBox' is the hub object that provides current API bindings (this object represents a particula virtualbox installation).

'objective' - provides higher-order command line bindings and completely parsed outputs.
'cli' - provides bindings to the virtual box command line interface. Performs initial output parsing -- splits output to fields.
'popen' - lowes layer, manages calling executables.
"""

from . import exceptions

from .vbox import VBox