import unittest
import safe_dill


class TestSafeLoads(unittest.TestCase):
    def test_try_to_reteive_sys(self):
        s = [b"\x80\x03csafe_dill.dill\nsys\nq\x00.",
            b"\x80\x03csys\nmodules\nq\x00."]
        for i in s:
            with self.subTest(s=s):
                with self.assertRaises(ImportError):
                    print(safe_dill.loads(i))

    def test_reteive_safe_func(self):
        s = b"\x80\x03csafe_dill.dill\n_import_module\nq\x00."
        self.assertEqual(safe_dill.loads(s), safe_dill.safe_dill._import_module)
