from . import base

from .mediums import HostMediums

class ResourceLibrary(base.ElementGroup):
    
    def getElements(self):
        return {
            "mediums": HostMediums(self),
        }