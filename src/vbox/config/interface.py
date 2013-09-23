class VirtualBox(object):

    def __init__(self, api):
        super(VirtualBox, self).__init__()
        self.api = api
        self.VM = VM(self.api)