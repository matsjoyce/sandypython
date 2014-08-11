import tcase
from sandypython.verify import *


class TestTypeChecker(tcase.TestCase):
    def setUp(self):
        class WierdObj:
            a = 1

        settypeverify(WierdObj, a=int, __module__=str, __doc__=(None, str),
                      __init__=Shared(WierdObj.__init__),
                      __weakref__=Shared(WierdObj.__weakref__),
                      __dict__=Shared(WierdObj.__dict__))
        setinstverify(WierdObj, __weakref__=None)

        class A:
            def __init__(self, a):
                self.a = 1

            def f(self):
                pass
            a = 1
            b = WierdObj()

        print(generatetypeverify(A))
        print(generateinstverify(A(1)))
        self.A = A
        self.WierdObj = WierdObj

    def test_arg_checker(self):
        @argschecker(a=(int, dict, list, None), b=str, c=str)
        def h(a, b, c=""):
            return str(a) + b + c

        with self.assertNotRaises():
            h(0, "", "")  # should work
        with self.assertRaises(RuntimeError):
            h(0, 0, "")
        # with self.assertRaises(RuntimeError):
        #     class str(__builtins__["str"]):
        #         pass
        #     __builtins__["str"] = str
        #     h(0, str(), "hi")
        with self.assertNotRaises():
            h(c="hoo", a=0, b="boo")
        with self.assertNotRaises():
            h(0, b="mushroom", c="crumple")
        with self.assertRaises(RuntimeError):
            h("", b="bear", c="sandbag")
        with self.assertNotRaises():
            h({}, b="box", c=" of sand")

        A, WierdObj = self.A, self.WierdObj

        @argschecker(a=(A, None), b=str, c=WierdObj)
        def h(a, b, c=WierdObj()):
            return 1, 2, 3

        with self.assertNotRaises():
            h(A(1), "")
        a = A(2)
        a.a = 5
        with self.assertNotRaises():
            h(a, "a")
        f = A.f
        A.f = self.test_verifyobj
        with self.assertRaises(RuntimeError):
            h(A(1), "hi")
        A.f = f
        WierdObj.a = 2
        with self.assertNotRaises():
            h(A(1), "hi")
            h(A(1), "hi", WierdObj())
        WierdObj.a = ""
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        WierdObj.a = 2

        A.f.x = 1
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        del A.f.x
        afm = A.f.__module__
        A.f.__module__ = WierdObj()
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        A.f.__module__ = afm

        @argschecker(__args__=Sequence(tuple, str), __kwargs__=str)
        def f(*args, **kwargs):
            pass

        with self.assertNotRaises():
            f()
        with self.assertNotRaises():
            f("a", "b")
        with self.assertNotRaises():
            f(a="a", b="b")
        with self.assertNotRaises():
            f("a", "b", "c", d="d", e="e")
        with self.assertRaises(RuntimeError):
            f(1, 2)
        with self.assertRaises(RuntimeError):
            f(a=1, d=2)
        with self.assertRaises(RuntimeError):
            f(1, 2, c=3, d=4)

    def test_arg_checker_ann(self):
        @argschecker_ann
        def h(a: (int, dict, list, None), b: str, c: str=""):
            return str(a) + b + c

        with self.assertNotRaises():
            h(0, "", "")  # should work
        with self.assertRaises(RuntimeError):
            h(0, 0, "")
        # with self.assertRaises(RuntimeError):
        #     class str(__builtins__["str"]):
        #         pass
        #     __builtins__["str"] = str
        #     h(0, str(), "hi")
        with self.assertNotRaises():
            h(c="hoo", a=0, b="boo")
        with self.assertNotRaises():
            h(0, b="mushroom", c="crumple")
        with self.assertRaises(RuntimeError):
            h("", b="bear", c="sandbag")
        with self.assertNotRaises():
            h({}, b="box", c=" of sand")

        A, WierdObj = self.A, self.WierdObj

        @argschecker_ann
        def h(a: (A, None), b: str, c: WierdObj=WierdObj()):
            return 1, 2, 3

        with self.assertNotRaises():
            h(A(1), "")
        a = A(2)
        a.a = 5
        with self.assertNotRaises():
            h(a, "a")
        f = A.f
        A.f = self.test_verifyobj
        with self.assertRaises(RuntimeError):
            h(A(1), "hi")
        A.f = f
        WierdObj.a = 2
        with self.assertNotRaises():
            h(A(1), "hi")
            h(A(1), "hi", WierdObj())
        WierdObj.a = ""
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        WierdObj.a = 2

        A.f.x = 1
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        del A.f.x
        afm = A.f.__module__
        A.f.__module__ = WierdObj()
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())
        A.f.__module__ = afm

        @argschecker_ann
        def f(*__args__: Sequence(tuple, str), **__kwargs__: str):
            pass

        with self.assertNotRaises():
            f()
        with self.assertNotRaises():
            f("a", "b")
        with self.assertNotRaises():
            f(a="a", b="b")
        with self.assertNotRaises():
            f("a", "b", "c", d="d", e="e")
        with self.assertRaises(RuntimeError):
            f(1, 2)
        with self.assertRaises(RuntimeError):
            f(a=1, d=2)
        with self.assertRaises(RuntimeError):
            f(1, 2, c=3, d=4)
