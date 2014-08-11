import unittest
import sandypython


class TestAttrRm(unittest.TestCase):
    def setUp(self):
        sandypython.core.add_default_builtins()

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

    def test_stats(self):
        sandypython.spec.stats()

    def tearDown(self):
        sandypython.core.reset()
