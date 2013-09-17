import logging
import unittest

class TestCLI(unittest.TestCase):

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.cli = vbox.VBox(['C:\Program Files\Oracle\VirtualBox']).cli

    def test_list_vms(self):
        self.assertIn("hdds", self.cli.manage.list())

    def test_list_vms(self):
        self.assertIn("hdds", self.cli.manage.list())

        for name in self.cli.manage.list():
            handle = getattr(self.cli.manage.list, name)            
            handle()

    def test_create_hd(self):
        print self.cli.manage.createHD("test", size="1024")