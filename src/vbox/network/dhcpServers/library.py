from .. import base

from .server import DhcpServer

class DhcpServerLibrary(base.VirtualBoxEntityType):
    
    cls = DhcpServer

    def listRegisteredIds(self):
        return (el["NetworkName"] for el in self.cli.manage.list.dhcpservers())