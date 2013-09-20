import os

import logging
import unittest

import time

class TestBound(unittest.TestCase):

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.api = vbox.VBox(['C:\Program Files\Oracle\VirtualBox'], debug=True).api

    def test_create_vm(self):
        api = self.api
        name = "{}_test_create_vms".format(self.__class__.__name__)
        vm = api.vms.new(name)
        oldMem = vm.memory
        oldAcpi = vm.acpi
        self.assertTrue(vm.registered)
        self.assertIn(oldAcpi, [True, False])
        assert vm.acpi in (True, False)

        vm.memory *= 2
        vm.acpi = not oldAcpi

        self.assertEqual(vm.memory, oldMem * 2)
        self.assertEqual(vm.acpi, not oldAcpi)

        vm.destroy()

    def test_hdd(self):
        api = self.api
        hdd = self.api.hdds.createNew(size=1024)
        self.assertTrue(hdd.UUID)
        hdd.destroy()

    def testControllerAccess(self):
        vm = self.api.vms.new("{}_testControllerAccess".format(self.__class__.__name__))
        print vm.source.info
        print vm.storageControllers.ide
        self.assertTrue(vm)
        self.assertTrue(vm.ide)
        self.assertTrue(vm.ide.findEmptySlot())
        self.assertTrue(vm.sata)
        self.assertTrue(vm.sata.findEmptySlot())
        self.assertTrue(vm.floppy)
        # destroy test
        vm.floppy.destroy()
        self.assertTrue(vm.floppy.findEmptySlot())
        1/0
        # vm.destroy()