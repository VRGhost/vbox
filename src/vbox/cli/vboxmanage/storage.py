"""
Storage medium-related commands.
"""

from .. import (
    base,
    util,
)

class ShowHdInfo(base.SubCommand):

    formatter = util.Formatter(
        all=("target", ),
        mandatory=("target", ),
        positional=("{target}", ),
    )
    outCheck = util.OutCheck(okRc=(0, 1))
    parser = util.parsers.Dict()

class CreateHD(base.SubCommand):

    formatter = util.Formatter(
        all=("filename", "size", "format", "variant"),
        mandatory=("filename", "size"),
    )
    outCheck = util.OutCheck(
        okRc=(0, ),
        extraChecks={
            0: lambda cmd, out: out and (not any(infix in out for infix in ("error:", "verr_"))),
        }
    )

class CloneHd(base.SubCommand):

    formatter = util.Formatter(
        all=("source", "destanation", "format", "variant", "existing"),
        mandatory=("source", "destanation"),
        flags=("existing", ),
        positional=("{source}", "{destanation}"),
    )

class StorageCtl(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "name", "add", "controller", "sataportcount", "hostiocache", "bootable", "remove"),
        positional=("target", ),
        mandatory=("target", "name"),
        flags=("remove", ),
        onOff=("hostiocache", "bootable"),
    )

class StorageAttach(base.SubCommand):

    formatter = util.Formatter(
        all=("target", "storagectl", "port", "device", "type", "medium"),
        mandatory=("target", "storagectl"),
        positional=("target", ),
    )

class CloseMedium(base.SubCommand):

    formatter = util.Formatter(
        all=("type", "target", "delete"),
        mandatory=("type", "target"),
        flags=("delete", ),
        positional=("{type}", "{target}"),
    )