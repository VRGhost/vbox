import functools
import os

import logging
import unittest

import time

def with_new_vm(func):
    @functools.wraps(func)
    def _wrapper(self):
        name = "{}_{}".format(self.__class__.__name__, func.__name__)
        vm = self.api.vms.getOrCreate(name)
        rv = func(self, vm)
        vm.destroy()
        return rv
    return _wrapper

class TestBound(unittest.TestCase):

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.api = vbox.VBox(['C:\Program Files\Oracle\VirtualBox'], debug=True).api

    @with_new_vm
    def test_create_vm(self, vm):
        oldMem = vm.memory
        oldAcpi = vm.acpi
        self.assertTrue(vm.registered)
        self.assertIn(oldAcpi, [True, False])
        assert vm.acpi in (True, False)

        vm.memory *= 2
        vm.acpi = not oldAcpi

        self.assertEqual(vm.memory, oldMem * 2)
        self.assertEqual(vm.acpi, not oldAcpi)

    def test_hdd(self):
        api = self.api
        hdd = self.api.hdds.create(size=1024)
        self.assertTrue(hdd.UUID)
        hdd.destroy()

    @with_new_vm
    def testChangeBootOrder(self, vm):
        old = tuple(vm.bootOrder)
        rev = tuple(reversed(old))
        vm.bootOrder = rev
        self.assertEqual(vm.bootOrder, rev)

    @with_new_vm
    def testControllerAccess(self, vm):
        controllers = vm.storageControllers
        controllers.ensureExist("ide")
        controllers.ensureExist("sata")
        controllers.ensureExist("floppy")

        self.assertTrue(controllers.ide)
        self.assertTrue(controllers.ide.findEmptySlot())
        self.assertTrue(controllers.sata)
        self.assertTrue(controllers.sata.findEmptySlot())
        self.assertTrue(controllers.floppy)
        # destroy test
        self.assertTrue(controllers.floppy.findEmptySlot())

    @with_new_vm
    def testHddAttach(self, vm):
        vm.storageControllers.ensureExist("ide")
        hdd = self.api.hdds.create(size=42)

        vm.storageControllers.ide.attach(hdd)
        slot = vm.storageControllers.ide.findSlotOf(hdd)
        hdd2 = vm.storageControllers.ide.slots[slot].medium
        self.assertEqual(hdd, hdd2)


    @with_new_vm
    def testEmptyDvdAttach(self, vm):
        img = self.api.dvds.empty
        vm.storageControllers.ensureExist("sata")

        vm.storageControllers.sata.attach(img)
        slot = vm.storageControllers.sata.findSlotOf(img)
        img2 = vm.storageControllers.sata.getMedia(slot)
        assert vm.storageControllers.sata.slots[slot].isEjectable in (True, False)
        self.assertEqual(img, img2)

    @with_new_vm
    def testEmptyFloppyAttach(self, vm):
        vm.storageControllers.ensureExist("floppy")
        img = self.api.floppies.empty
        controller = vm.storageControllers.floppy

        controller.attach(img)
        slot = controller.findSlotOf(img)
        img2 = controller.getMedia(slot)
        self.assertEqual(img, img2)