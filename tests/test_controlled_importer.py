import unittest
import sandypython


class TestControlledImporter(unittest.TestCase):
    def test_controlled_importer_noise(self):
        imap = {"default": ["sys", "io"],
                "test_controlled_importer.py": ["os"]
                }
        f = sandypython.utils.checked_importer(imap, noise=True)
        f("sys")
        f("io")
        f("os")
        with self.assertRaises(ImportError):
            f("functools")

    def test_controlled_importer(self):
        imap = {"default": ["sys", "io"],
                "test_controlled_importer.py": ["os"]
                }
        f = sandypython.utils.checked_importer(imap)
        f("sys")
        f("io")
        f("os")
        with self.assertRaises(ImportError):
            f("functools")
