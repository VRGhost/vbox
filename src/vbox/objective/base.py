class Base(object):

    def __init__(self, interface):
        super(Base, self).__init__()
        self.interface = interface
        self.cli = self.interface.cli

class Library(Base):
    pass