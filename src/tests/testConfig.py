import functools
import os

import logging
import unittest

import time

FD_IMG=os.path.realpath(os.path.join(os.path.dirname(__file__), "fd.img"))

class TestConfig(unittest.TestCase):
    """This helps to test VM creation out of dict configs."""

    def setUp(self):
        import vbox
        logging.basicConfig(level=logging.DEBUG)
        self.vbox = vbox.VBox.fromDict({
            "extraPath": ['C:\Program Files\Oracle\VirtualBox'],
            "debug": True
        })


    def testBasicVm(self):
        cfg = {
            "name": "foo",
            "osType": "Windows95",
            "memory": 12,
            "accelerate3d": False,
            "videoMemory": 12,
            "media": {
                "ide": {
                    "targets": [
                        {"type": "hdd", "size": 42},
                        {"type": "dvd"},
                    ],
                },
                "floppy": {
                    "bootable": True,
                    "targets": [
                        {
                            "target": FD_IMG
                        },
                    ],
                },
                "sata": {},
            },
        }
        vm = self.vbox.config.VM.fromDict(cfg, force=1)
        vm.destroy()