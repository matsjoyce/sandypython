import unittest
from sandypython.verify import *


class TestVerify(unittest.TestCase):
    def assertNotRaises(self):
        class NR:
            def __init__(self, master):
                self.master = master

            def __enter__(self):
                pass

            def __exit__(self, type, value, traceback):
                if type:
                    self.master.fail("It raised a {}({})".format(type, value))
        return NR(self)

    def setUp(self):
        class WierdObj:
            a = 1

        settypeverify(WierdObj, a=int, __module__=str, __doc__=(None, str), __init__=Shared(WierdObj.__init__), __weakref__=Shared(WierdObj.__weakref__), __dict__=Shared(WierdObj.__dict__))
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

    def test_verifyobj(self):
        A, WierdObj = self.A, self.WierdObj
        self.assertIs(verifyobj(A(1)), None)
        a = A(2)
        a.a = 5
        self.assertIs(verifyobj(a), None)
        a.a = ""
        self.assertEqual(verifyobj(a), ("key 'a' has failed verification", a))
        f = A.f
        A.f = self.test_verifyobj
        self.assertEqual(verifyobj(A(1)), ("key 'f' has failed verification", A))
        A.f = f
        WierdObj.a = 2
        self.assertIs(verifyobj(A(1)), None)
        WierdObj.a = ""
        self.assertEqual(verifyobj(A(1)), ("key 'a' has failed verification", WierdObj))
        WierdObj.a = 2

        def f():
            pass

        self.assertIs(verifyobj(f), None)
        f.x = 1
        self.assertEqual(verifyobj(f), ("key 'x' not in verify data", f))
        del f.x
        f.__module__ = WierdObj()
        self.assertEqual(verifyobj(f), ("key '__module__' has failed verification", f))

    def test_arg_checker(self):
        @argschecker(a=(int, dict, list, None), b=str, c=str)
        def h(a, b, c=""):
            return str(a) + b + c

        with self.assertNotRaises():
            h(0, "", "")  # should work
        with self.assertRaises(RuntimeError):
            h(0, 0, "")
        #with self.assertRaises(RuntimeError):
            #class str(__builtins__["str"]):
                #pass
            #__builtins__["str"] = str
            #h(0, str(), "hi")
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
        A.f.__module__ = WierdObj()
        with self.assertRaises(RuntimeError):
            h(A(1), "hi", WierdObj())

if __name__ == "__main__":
    tv = TestVerify()
    tv.setUp()
    tv.test_verifyobj()
    tv.test_arg_checker()
