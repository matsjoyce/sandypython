import unittest
import sandypython


class TestAttrRm(unittest.TestCase):
    def setUp(self):
        sandypython.core.allow_defaults()

    def test_func_globals(self):
        with self.assertRaises(AttributeError):
            with sandypython.utils.ActivateSandbox():
                self.setUp.__globals__

    def test_all(self):
        with sandypython.utils.ActivateSandbox():
            pass
        for type, attr in sandypython.spec.saved:
            with self.subTest(type=type, attr=attr):
                with self.assertRaises(AttributeError):
                    with sandypython.utils.ActivateSandbox():
                        getattr(type, attr)

    def tearDown(self):
        sandypython.core.reset()
