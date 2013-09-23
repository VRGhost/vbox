import functools
import os

import logging
import unittest

import time


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
        vm = self.vbox.config.VM.fromDict({
            "name": "foo",
            "osType": "Windows95",
            "memory": 12,
            "accelerate3d": False,
            "videoMemory": 12,
            "storage": {
                "hdd": {"size": 42, "controller": "sata"},
                "dvd": {"controller": "ide"},
                "fdd": {},
            }
        }).ensure()