"""manage list command."""

import re

from .. import (
    base,
    util,
)

class ListVmsParser(util.parsers.Dict):


    def _parseItems(self, output):
        dequote = self.dequote
        # Parse lines of format '''"name" {uid}'''
        for line in output.splitlines():
            if " {" not in line:
                continue
            (name, uid) = line.strip().split(" {", 1)
            yield (
                dequote(name),
                uid.rstrip('}'),
            )

def gen_list_check(*args):
    def _check(cmd, out):
        return (len(cmd) == 2) and (cmd[0] == "list") and (cmd[1] in args)
    return _check

def SPLIT_ALL(args, output):
    oneLine = "".join(line.strip() for line in output.splitlines())
    match = re.search(r"(\w+(?:\|\w+)+)", oneLine)
    return tuple(match.group(1).split('|'))

class List(base.SubCommand):

    formatter = util.Formatter(
        all=("what", ),
        positional=("{what}", ),
        mandatory=(),
    )
    outCheck = util.OutCheck(
        okRc=(0, 1),
        extraChecks={
            1: lambda args, out: args == ("list", ), # RC 1 is ok only for 'VBoxManage list' call
        }
    )
    parser = util.parsers.Conditional([
        (lambda cmd, out: cmd == ("list", ), SPLIT_ALL),
        (gen_list_check(
            "hdds", "ostypes", "hostdvds", "hostfloppies",
            "bridgedifs", "hostonlyifs", "dhcpservers",
            "dvds", "floppies", "usbhost",
            ), util.parsers.Dicts()),
        (gen_list_check(
            "hostinfo", "systemproperties",
            ), util.parsers.Dict()),
        (gen_list_check("groups"), util.parsers.Strings()),
        (gen_list_check("vms", "runningvms"), ListVmsParser()),
        (gen_list_check("hostcpuids", "hddbackends", "usbfilters", "extpacks", "groups"), util.parsers.Dummy())
    ])



    bridgedifs = lambda s: s("bridgedifs")
    dhcpservers = lambda s: s("dhcpservers")
    dvds = lambda s: s("dvds")
    extpacks = lambda s: s("extpacks")
    floppies = lambda s: s("floppies")
    groups = lambda s: s("groups")
    hddbackends = lambda s: s("hddbackends")
    hdds = lambda s: s("hdds")
    hdds = lambda s: s("hdds")
    hostcpuids = lambda s: s("hostcpuids")
    hostdvds = lambda s: s("hostdvds")
    hostfloppies = lambda s: s("hostfloppies")
    hostinfo = lambda s: s("hostinfo")
    hostonlyifs = lambda s: s("hostonlyifs")
    ostypes = lambda s: s("ostypes")
    runningvms = lambda s: s("runningvms")
    systemproperties = lambda s: s("systemproperties")
    usbfilters = lambda s: s("usbfilters")
    usbhost = lambda s: s("usbhost")
    vms = lambda s: s("vms")