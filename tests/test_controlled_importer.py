import unittest
import sandbox


class TestControlledImporter(unittest.TestCase):
    def test_controlled_importer(self):
        imap = {"default": ["sys", "io"],
                "test_controlled_importer.py": ["os"]
                }
        f = sandbox.checked_importer(imap, noise=True)
        f("sys")
        f("io")
        f("os")
        with self.assertRaises(ImportError):
            f("functools")
