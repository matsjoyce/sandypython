import unittest
from sandypython.utils import type_checker, type_checker_annotated, Any


class TestTypeChecker(unittest.TestCase):
    @type_checker(self=Any, a=(int, dict, list, None), b=str,
                  c=str, d=None)
    def f(self, a, b, c="", d=None):
        return str(a) + b + c

    @type_checker_annotated
    def f_ann(self: Any, a: (int, dict, list, None), b: str, c: str="",
              d: None=None):
        return str(a) + b + c

    def do_test(self, f):
        f(0, "", "")  # should work

        f(None, "", "")  # should work

        with self.assertRaises(TypeError):
            f(0, 0, "")

        with self.assertRaises(TypeError):
            class str(__builtins__["str"]):
                pass
            __builtins__["str"] = str
            f(0, str(), "hi")

        f(c="hoo", a=0, b="boo", d=None)  # should work
        f(0, b="mushroom", c="crumple")  # should work

        with self.assertRaises(TypeError):
            f("", b="bear", c="sandbag")

        with self.assertRaises(TypeError):
            f([], "", d=1)

        f({}, b="box", c=" of sand")  # should work

    def test_type_checker(self):
        self.do_test(self.f)

    def test_type_checker_ann(self):
        self.do_test(self.f_ann)
