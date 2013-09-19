import os

import logging
import unittest

import time

class TestBound(unittest.TestCase):

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.bound = vbox.VBox(['C:\Program Files\Oracle\VirtualBox'], debug=True).bound

    def test_create_vm(self):
        vms = self.bound.vms
        name = "{}_vm_test".format(self.__class__.__name__)

        self.assertFalse(name in vms)
        vm = self.bound.vms.new(name)
        vm.create()
        self.assertTrue(name in vms)
        vm.info
        self.assertNotEqual(vm.info["memory"], "123")
        vm.modify(memory="123")
        self.assertEqual(vm.info["memory"], "123")

        vm.start()
        vm.poweroff()
        time.sleep(2)

        vm.destroy()
        self.assertFalse(name in vms)

    def test_vm_list(self):
        self.bound.vms.listRegistered()