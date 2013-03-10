from .. import base

VirtualBoxEntity = base.VirtualBoxEntity

class Refreshable(object):
    
    refreshPending = True

    def refresh(self):
        del self.info
        self.info

class OnCallRefresher(object):

    def __init__(self, parent, target):
        self.parent = parent
        self.target = target

    def __getattr__(self, name):
        obj = self.__class__(self.parent, getattr(self.target, name))
        setattr(self, name, obj)
        return obj

    def __call__(self, *args, **kwargs):
        rv = self.target(*args, **kwargs)
        self.parent.refresh()
        return rv

class RefreshableEntity(VirtualBoxEntity, Refreshable):
    
    class cli(object):
        manage = None

    def __init__(self, *args, **kwargs):
        super(RefreshableEntity, self).__init__(*args, **kwargs)
        self.cli.manage = OnCallRefresher(self, self.vb.cli.manage)

class VirtualMachinePart(RefreshableEntity):
    
    def __init__(self, vm, *args, **kwargs):
        super(VirtualMachinePart, self).__init__(*args, **kwargs)
        self.vm = vm

    def refresh(self):
        self.parent.refresh()
        super(VirtualMachinePart, self).refresh()