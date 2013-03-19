import unittest
import time

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
                api.DVD(),
                api.FDD(),
            )
        )
        vm.start()
        vm.wait(2)
        vm.powerOff()