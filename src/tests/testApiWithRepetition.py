import functools
import os

import logging
import unittest

import time

FD_IMG=os.path.realpath(os.path.join(os.path.dirname(__file__), "fd.img"))

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
    """Ali-level tests than can cause repeated CLI commands to be issued.

    Hence, the CLI duplicate command detection is disabled here.
    """

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.api = vbox.VBox(['C:\Program Files\Oracle\VirtualBox']).api


    @with_new_vm
    def testFdBoot(self, vm):
        img = self.api.floppies.fromFile(FD_IMG)
        vm.storageControllers.ensureExist("floppy")
        controller = vm.storageControllers.floppy

        controller.attach(img, bootable=True)
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


    def testDoubleDestroy(self):
        name = "{}_testDoubleDestroy".format(self.__class__.__name__)
        vm = self.api.vms.new(name)
        vm.destroy()
        with self.assertRaises(vm.exceptions.VmNotFound):
            vm.destroy()