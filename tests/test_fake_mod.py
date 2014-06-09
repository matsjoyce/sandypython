import unittest
from sandypython.fakemod import make_fake_mod


class TestFakeMod(unittest.TestCase):
    def test_fake_mod(self):
        f = make_fake_mod({"a": 1, "b": {}, "c": self})
        self.assertEqual(f.a, 1)
        self.assertEqual(f.b, {})
        self.assertEqual(f.c, self)
        with self.assertRaises(AttributeError):
            f.d
