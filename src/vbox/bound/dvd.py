from . import base

class DVD(base.Entity):
    pass
    
class Library(base.Library):

    entityCls = DVD