from . import base

class HostOnlyInterface(base.Entity):

    @base.refreshedProperty
    def info(self):
        for el in self.library.hostOnlyInterfacesSource:
            if el["Name"] == self.id:
                return dict(el)
        raise self.exceptions.BoundError("No {!r} interface found".format(self.id))

    @base.refreshingLib
    def remove(self):
        self.cli.manage.hostOnlyIf.remove(self.id)

    @base.refreshingLib
    def set(self, **kwargs):
        self.cli.manage.hostOnlyIf(target=self.id, action="ipconfig", **kwargs)


class Library(base.Library):

    @base.refreshedProperty
    def hostOnlyInterfacesSource(self):
        return self.cli.manage.list.hostonlyifs()

    @base.refreshedProperty
    def hostOnlyInterfaces(self):
        return tuple(HostOnlyInterface(self, el["Name"]) for el in self.hostOnlyInterfacesSource)

    @base.refreshedProperty
    def bridgedInterfaces(self):
        return self.cli.manage.list.bridgedifs()

    @base.refreshedProperty
    def dhcpServers(self):
        return self.cli.manage.list.dhcpservers()

    @base.refreshing
    def createHostOnlyInterface(self):
        name = self.cli.manage.hostOnlyIf.create()
        return HostOnlyInterface(self, name)