from . import base
from .. import util

class NIC(base.VirtualBoxObject):

    name = util.props.String("Name")
    guid = util.props.String("GUID")
    ip = util.props.String("IPAddress")
    mask = util.props.String("NetworkMask")
    ipv6 = util.props.String("IPV6Address")
    ipv6MaskLen = util.props.Int("IPV6NetworkMaskPrefixLength")
    type = util.props.String("MediumType")
    networkName = util.props.String("VBoxNetworkName")

    mac = base.ColonSeparatedMac("HardwareAddress")
    configuredWithDhcp = base.EnabledDisabled("DHCP")
    operational = base.UpDown("Status")

    dhcpServer = property(lambda s: s.vb.net.dhcpServers.find(s.networkName))

    
    def _getInfo(self):
        _id = self._initId
        for rec in self._getIfList():
            if rec["Name"] == _id:
                return rec
        else:
            raise Exception("Interface {!r} not found".format(_id))
        assert found

    def _getIfList(self):
        raise NotImplementedError

class HostOnlyNic(NIC):

    _getIfList = lambda s: s.cli.manage.list.hostonlyifs()

class BridgedNic(NIC):

    _getIfList = lambda s: s.cli.manage.list.bridgedifs()