import unittest

from vbox import api

class TestExtApi(unittest.TestCase):

    def testWrongConfigVm(self):
        self.assertRaises(ValueError, api.VM)
        self.assertRaises(ValueError, api.General, name="foo")

    def testBasicVm(self):
        vm = api.VM(
            api.General(
                name="foo",
                osType="Windows95",
            ),
            api.System(
                memory=12,
            ),
            api.Storage(
                api.HDD(size=10*1024),
                api.DVD(
                    target=r"C:\Users\e102308\Documents\ISOs\CentOS-6.3-x86_64-bin-DVD1.iso"
                ),
            )
        )
        vm.system.memory *= 2
        print vm.system.memory
        print vm.storage.dvd
        self.assertGreater(vm.system.memory, 0)