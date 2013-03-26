"""External API vbox library."""

from .virtualbox import VirtualBox
from .vm import VM
from .general import DetachedGeneral as General
from .system import System, CPU
from .display import Display
from .storage import Storage, HDD, DVD, FDD
from .network import Network, NIC