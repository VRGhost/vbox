import os

import unittest

class TestVirtualBox(unittest.TestCase):

    def setUp(self):
        import vbox
        self.vb = vbox.VirtualBox()

    def testListAll(self):
        listAll = self.vb.list.all()
        self.assertIn("hdds", listAll)
        self.assertIn("dvds", listAll)

    def testListOsTypes(self):
        listAll = self.vb.list.ostypes()
        descs = [el["Description"] for el in listAll]
        self.assertIn("Windows 95", descs)
        self.assertIn("Ubuntu", descs)

    def testCreateHdd(self):
        size = 10 * 1024
        hdd = self.vb.hdd.create(size=size)
        self.assertEqual(hdd.size, size)
        fname = hdd.fname
        hdd.destroy()
        self.assertFalse(hdd.info)
        self.assertFalse(hdd.size)
        self.assertFalse(os.path.exists(fname))

    def testSystemInfo(self):
        info = self.vb.info.system
        self.assertTrue(info)

    def testHostInfo(self):
        self.assertTrue(self.vb.info.host)

    def testCreateVmRecord(self):
        vm = self.vb.vms.create(register=True)
        self.assertTrue(vm)
        self.assertIn(vm, self.vb.vms.list())
        vm.destroy()
        self.assertNotIn(vm, self.vb.vms.list())

    def testControllerAccess(self):
        vm = self.vb.vms.create(register=True)
        self.assertTrue(vm)
        self.assertTrue(vm.ide)
        self.assertTrue(vm.ide.findEmptySlot())
        self.assertTrue(vm.sata)
        self.assertTrue(vm.sata.findEmptySlot())
        self.assertTrue(vm.floppy)
        # destroy test
        vm.floppy.destroy()
        self.assertTrue(vm.floppy.findEmptySlot())
        vm.destroy()

    def testHddAttach(self):
        vm = self.vb.vms.create(register=True)
        hdd = self.vb.hdd.create(size=42)
        vm.ide.attach(hdd)
        print(vm.ide.findSlotOf(hdd))
        vm.destroy()