from .. import base

class DhcpServer(base.VirtualBoxObject):

    name = property(lambda s: s.getProp("NetworkName"))
    
    def _getInfo(self):
        _id = self._initId
        for rec in self.cli.manage.list.dhcpservers():
            if rec["NetworkName"] == _id:
                return rec
        else:
            raise Exception("Interface {!r} not found".format(_id))
