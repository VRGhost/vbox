from . import base

class Floppy(base.Entity):
    pass

class Library(base.Library):
    
    entityCls = Floppy