from . import base

class Library(base.Library):

    @base.refreshedProperty
    def hostOnlyInterfaces(self):
        return self.cli.manage.list.hostonlyifs()

    @base.refreshedProperty
    def bridgedInterfaces(self):
        return self.cli.manage.list.bridgedifs()

    @base.refreshedProperty
    def dhcpServers(self):
        return self.cli.manage.list.dhcpservers()