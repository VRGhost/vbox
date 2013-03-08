import unittest

class TestBasicImport(unittest.TestCase):

    def test_import_root_pkg(self):
        import vbox
        self.assertTrue(vbox)
        self.assertTrue(vbox.VirtualBox)