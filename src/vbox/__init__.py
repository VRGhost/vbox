"""VBox project uses layered architecture

'VBox' is the hub object that provides current API bindings (this object represents a particula virtualbox installation).

'bound' - objective bindings to CLI handlers. This layer server two purposes:
    1) Provide initial objective API;
    2) Provide caching (nether 'cli' or 'popen' should do any caching);
'cli' - provides bindings to the virtual box command line interface. Performs initial output parsing -- splits output to fields.
'popen' - lowes layer, manages calling executables.
"""

from . import exceptions

from .vbox import VBox