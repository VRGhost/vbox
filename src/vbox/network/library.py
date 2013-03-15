from . import base, interface


from .dhcpServers import DhcpServerLibrary

class HostOnlyInterfaceLibrary(base.VirtualBoxEntityType):

    cls = interface.HostOnlyNic
    
    def listRegisteredIds(self):
        return (el["Name"] for el in self.cli.manage.list.hostonlyifs())

class BridgedInterfaceLibrary(base.VirtualBoxEntityType):

    cls = interface.BridgedNic

    def listRegisteredIds(self):
        return (el["Name"] for el in self.cli.manage.list.bridgedifs())

class NetworkLibrary(base.ElementGroup):

    def getElements(self):
        return {
            "hostOnlyInterfaces": HostOnlyInterfaceLibrary(self),
            "bridgedInterfaces": BridgedInterfaceLibrary(self),
            "dhcpServers": DhcpServerLibrary(self),
        }