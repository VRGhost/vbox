import logging
import os
import time
import unittest

FD_IMG=os.path.realpath(os.path.join(os.path.dirname(__file__), "fd.img"))

class TestVirtualBox(unittest.TestCase):

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.vb = vbox.VirtualBox()

    def testListAll(self):
        listAll = self.vb.cli.manage.list.all()
        self.assertIn("hdds", listAll)
        self.assertIn("dvds", listAll)

    def testListOsTypes(self):
        listAll = self.vb.cli.manage.list.ostypes()
        descs = [el["Description"] for el in listAll]
        self.assertIn("Windows 95", descs)
        self.assertIn("Ubuntu", descs)

    def testCreateHdd(self):
        size = 10 * 1024
        hdd = self.vb.hdd.create(size=size)
        self.assertEqual(hdd.size, size)
        fname = hdd.fname
        hdd.destroy()
        self.assertFalse(hdd.accessible)
        self.assertFalse(os.path.exists(fname))

    def testSystemInfo(self):
        info = self.vb.info.system
        self.assertTrue(info)

    def testHostInfo(self):
        self.assertTrue(self.vb.info.host)

    def testCreateVmRecord(self):
        ostypes = self.vb.info.ostypes
        for el in ostypes:
            if ("other" in el["Description"].lower()) or \
                ("unknown" in el["Description"].lower()):
                continue

            if el["Description"] != el["ID"]:
                # Picking more ostype that is as cunning as possible
                selected = el
                break
        else:
            selected = ostypes[-1]

        checkTypeDesc = selected["Description"]
        checkTypeId = selected["ID"]
        vm = self.vb.vms.create(register=True, ostype=checkTypeDesc)
        self.assertTrue(vm)
        self.assertIn(vm, self.vb.vms.list())
        self.assertEqual(vm.ostype, checkTypeId)
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
        img = self.vb.resources.mediums.dvd.empty
        vm.ide.attach(img)
        (device, port) = vm.ide.findSlotOf(img)
        img2 = vm.ide.getMedia(device, port)
        self.assertEqual(img, img2)
        vm.destroy()

    def testEmptyFloppyAttach(self):
        vm = self.vb.vms.create(register=True)
        img = self.vb.resources.mediums.floppy.empty
        vm.floppy.attach(img)
        (device, port) = vm.floppy.findSlotOf(img)
        img2 = vm.floppy.getMedia(device, port)
        self.assertEqual(img, img2)
        vm.destroy()

    def testFdBoot(self):
        vm = self.vb.vms.create(register=True)
        img = self.vb.resources.mediums.floppy.get(FD_IMG)
        vm.floppy.attach(img, ensureBootable=True)
        self.assertFalse(vm.state.running)
        oldTime = vm.changeTime
        vm.state.start()
        self.assertTrue(vm.state.running)
        vm.wait(timeout=2)
        # this FD image simply stays turned on.
        self.assertTrue(vm.state.running)
        vm.state.pause()
        self.assertFalse(vm.state.running)
        self.assertTrue(vm.state.paused)
        vm.state.resume()
        self.assertTrue(vm.state.running)
        # Reset
        vm.state.reset()
        self.assertTrue(vm.state.running)
        vm.state.powerOff()
        self.assertGreater(vm.changeTime, oldTime)
        self.assertFalse(vm.state.running)
        vm.destroy()

    def testChangeVmProps(self):
        vm = self.vb.vms.create(register=True)
        vm.memory = 512
        self.assertEqual(vm.memory, 512)
        vm.destroy()

    def testNicAttach(self):
        vm = self.vb.vms.create(register=True)
        nic = vm.nics[1]
        self.assertEqual(nic.type, None)
        nic.type = "hostonly"
        self.assertEqual(nic.type, "hostonly")
        self.assertEqual(len(nic.mac), 12)
        nic.cableConnected = True
        self.assertTrue(vm.nics[1].cableConnected)
        nic.cableConnected = False
        self.assertFalse(vm.nics[1].cableConnected)
        vm.destroy()

    def testSimpleCloneVm(self):
        vm = self.vb.vms.create(register=True)
        self.assertTrue(vm.registered)
        vm2 = vm.clone(name="Clone of {parent.name}.")
        expectedName = "Clone of {}.".format(vm.name)
        self.assertEqual(vm2.name, expectedName)
        self.assertTrue(vm2.registered)
        vm.destroy()
        vm2.destroy()
        
    def testCloneVmOptions(self):
        vm = self.vb.vms.create(register=True)
        hdd = self.vb.hdd.create(size=42)
        self.assertTrue(hdd.name)
        hddSlot = vm.ide.attach(hdd)

        vm.nics[1].type = "hostonly"
        origMac = vm.nics[1].mac
        self.assertEqual(len(origMac), 12)
        # Clone with no preservation of anything
        vm2 = vm.clone()
        self.assertEqual(len(vm2.nics[1].mac), 12)
        self.assertNotEqual(vm2.nics[1].mac, origMac)
        hdd2 = vm2.ide.getMedia(*hddSlot)
        self.assertTrue(hdd2)
        self.assertTrue(hdd2.name)
        self.assertNotEqual(hdd2.name, hdd.name)
        vm2.destroy()
        # Clone and preserve MAC, but not HDD name
        vm3 = vm.clone(options=["keepallmacs", ])
        self.assertEqual(len(vm3.nics[1].mac), 12)
        self.assertEqual(vm3.nics[1].mac, origMac)
        hdd2 = vm3.ide.getMedia(*hddSlot)
        self.assertTrue(hdd2)
        self.assertTrue(hdd2.name)
        self.assertNotEqual(hdd2.name, hdd.name)
        vm3.destroy()
        # Clone and preserve MAC and HDD name
        vm4 = vm.clone(options=["keepallmacs", "keepdisknames"])
        self.assertEqual(len(vm4.nics[1].mac), 12)
        self.assertEqual(vm4.nics[1].mac, origMac)
        hdd2 = vm4.ide.getMedia(*hddSlot)
        self.assertTrue(hdd2)
        self.assertTrue(hdd2.name)
        self.assertEqual(hdd2.name, hdd.name)
        vm4.destroy()
        
        vm.destroy()

    def testAAOnlineNicControlChanges(self):
        vm = self.vb.vms.create(register=True)

        img = self.vb.resources.mediums.floppy.get(FD_IMG)
        vm.floppy.attach(img, ensureBootable=True)

        print tuple(el.type for el in vm.nics)

        vm.nics[1].type = "hostonly"
        vm.cableConnected = True
        self.assertTrue(vm.cableConnected)
        vm.cableConnected = False
        self.assertFalse(vm.cableConnected)

        vm.state.start()
        self.assertTrue(vm.state.running)

        vm.cableConnected = True
        self.assertTrue(vm.cableConnected)
        vm.cableConnected = False
        self.assertFalse(vm.cableConnected)
        vm.nics[1].type = "intnet"
        self.assertEqual(vm.nics[1].type, "intnet")
        vm.cableConnected = True
        self.assertTrue(vm.cableConnected)
        vm.cableConnected = False
        self.assertFalse(vm.cableConnected)

        
        1/0
        vm.destroy()