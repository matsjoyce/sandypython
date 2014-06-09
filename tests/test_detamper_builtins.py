import unittest
import sandypython


class TestDetampBuiltins(unittest.TestCase):
    def setUp(self):
        sandypython.core.allow_defaults()
        sandypython.core.replace_builtin("divmod", "any")

    def test_detamp_builtins(self):
        sandypython.core.save_restricted()
        sandypython.core.restore_restricted()
        s = str

        class S:
            pass

        sandypython.core.detamper_builtins(force=True)
        with self.assertRaises(NameError):
            print()

        __builtins__["str"] = S
        __builtins__["print"] = self.setUp()
        __builtins__["divmod"] = "l"

        sandypython.core.detamper_builtins(force=True)

        self.assertEqual(str, s)
        self.assertEqual(divmod, "any")
        with self.assertRaises(NameError):
            print()

        sandypython.core.restore_restricted()

    def tearDown(self):
        sandypython.core.reset()
