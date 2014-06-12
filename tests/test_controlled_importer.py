import unittest
import sys
from sandypython.utils import *


class TestControlledImporter(unittest.TestCase):
    def test_controlled_importer_noise(self):
        imap = {"default": ["sys", "io"],
                __file__: ["os"]
                }
        f = checked_importer(import_filter_by_name(imap), noise=True)
        f("sys")
        f("io")
        f("os")
        with self.assertRaises(ImportError):
            f("functools")

    def test_controlled_importer(self):
        imap = {"default": ["./tests/a_mod*"],
                __file__: ["./tests/*.py"]
                }
        f = checked_importer(import_filter_by_path(imap))
        f("a_mod")
        f("test_fake_mod")
        with self.assertRaises(ImportError):
            f("sys")
        with self.assertRaises(ImportError):
            f("kivy")
