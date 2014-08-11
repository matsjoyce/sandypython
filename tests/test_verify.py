import unittest
from sandypython.verify import *


class TestVerify(unittest.TestCase):
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
        self.assertEqual(verifyobj(A(1)), ("key 'f' has failed verification",
                                           A))
        A.f = f
        WierdObj.a = 2
        self.assertIs(verifyobj(A(1)), None)
        WierdObj.a = ""
        self.assertEqual(verifyobj(A(1)), ("key 'a' has failed verification",
                                           WierdObj))
        WierdObj.a = 2

        def f():
            pass

        self.assertIs(verifyobj(f), None)
        f.x = 1
        self.assertEqual(verifyobj(f), ("key 'x' not in verify data", f))
        del f.x
        f.__module__ = WierdObj()
        self.assertEqual(verifyobj(f), ("key '__module__' has failed "
                                        "verification", f))

if __name__ == "__main__":
    tv = TestVerify()
    tv.setUp()
    tv.test_verifyobj()
    tv.test_arg_checker()
    tv.test_arg_checker_ann()
