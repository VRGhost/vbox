from . import (
    base,
    hdd,
)

class HddLibrary(base.VirtualBoxEntityType):
    """HDD interface."""

    cls = hdd.HDD

    def create(self, size, filename=None, autoname=True, format="VDI", variant="Standard"):
        super(_HDD, self).create()
        if autoname:
            lst = tuple(self.list())
            idx = 0
            prefix = filename or "auto_created_hdd"
            genName = lambda : "{}_{}.{}".format(prefix, idx, format.lower())
            while (genName() in lst) or os.path.exists(genName()):
                idx += 1
            assert genName() not in lst
            filename = genName()

        createhd = lambda: self.vb.cli.manage.createhd(
            filename=filename, size=size, format=format, variant=variant)
        hddExistsMsg = "cannot register the hard disk"
        hddExistsError = False

        try:
            createhd()
        except cli.CmdError as err:
            if autoname and (hddExistsMsg in err.output.lower()):
                hddExistsError = True
            else:
                raise

        if hddExistsError:
            assert autoname
            assert genName

            while hddExistsError:
                # remove old file, if it was created
                if os.path.exists(filename):
                    os.unlink(filename)
                idx += 1
                filename = genName()
                try:
                    createhd()
                except cli.CmdError as err:
                    if hddExistsMsg in err.output.lower():
                        continue
                    raise
                else:
                    # creation succeeded
                    break

        return self.get(filename)

    def listRegisteredIds(self):
        return [el["UUID"] for el in self.vb.cli.manage.list.hdds()]