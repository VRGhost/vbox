import os
import time
import unittest

FD_IMG=os.path.realpath(os.path.join(os.path.dirname(__file__), "fd.img"))

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
        (device, port) = vm.ide.findSlotOf(hdd)
        hdd2 = vm.ide.getMedia(device, port)
        self.assertEqual(hdd, hdd2)
        vm.destroy()

    def testEmptyDvdAttach(self):
        vm = self.vb.vms.create(register=True)
        img = self.vb.mediums.dvd.empty
        vm.ide.attach(img)
        (device, port) = vm.ide.findSlotOf(img)
        img2 = vm.ide.getMedia(device, port)
        self.assertEqual(img, img2)
        vm.destroy()

    def testEmptyFloppyAttach(self):
        vm = self.vb.vms.create(register=True)
        img = self.vb.mediums.floppy.empty
        vm.floppy.attach(img)
        (device, port) = vm.floppy.findSlotOf(img)
        img2 = vm.floppy.getMedia(device, port)
        self.assertEqual(img, img2)
        vm.destroy()

    def testFdBoot(self):
        vm = self.vb.vms.create(register=True)
        img = self.vb.mediums.floppy.get(FD_IMG)
        vm.floppy.attach(img)
        self.assertFalse(vm.running)
        vm.start()
        self.assertTrue(vm.running)
        vm.wait(timeout=2)
        # this FD image simply stays turned on.
        self.assertTrue(vm.running)
        vm.pause()
        self.assertFalse(vm.running)
        self.assertTrue(vm.paused)
        vm.resume()
        self.assertTrue(vm.running)
        # Reset
        vm.reset()
        self.assertTrue(vm.running)
        vm.powerOff()
        self.assertFalse(vm.running)
        #vm.destroy()