from . import base

refreshing = base.refreshing

class HDD(base.Entity):
    pass

class Library(base.Library):

    entityCls = HDD

    def new(self, filename, size, format=None, variant=None):
        1/0

    # @base.refreshed
    # def listRegistered(self):
    #