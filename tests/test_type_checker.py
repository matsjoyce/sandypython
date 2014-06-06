import unittest
import sandbox


class TestTypeChecker(unittest.TestCase):
    @sandbox.type_checker(self=sandbox.Any, a=(int, dict, list, None), b=str,
                          c=str, d=None)
    def f(self, a, b, c="", d=None):
        return str(a) + b + c

    def test_type_checker(self):
        self.f(0, "", "")  # should work

        self.f(None, "", "")  # should work

        with self.assertRaises(TypeError):
            self.f(0, 0, "")

        with self.assertRaises(TypeError):
            class str(__builtins__["str"]):
                pass
            __builtins__["str"] = str
            self.f(0, str(), "hi")

        self.f(c="hoo", a=0, b="boo", d=None)  # should work
        self.f(0, b="mushroom", c="crumple")  # should work

        with self.assertRaises(TypeError):
            self.f("", b="bear", c="sandbag")

        with self.assertRaises(TypeError):
            self.f([], "", d=1)

        self.f({}, b="box", c=" of sand")  # should work
