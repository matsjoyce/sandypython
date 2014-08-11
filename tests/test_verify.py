import tcase
import re
from sandypython.verify import *


class TestVerify(tcase.TestCase):
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
        self.assertIs(verifyobj(A), None)
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

    def test_shared_matcher(self):
        def f():
            pass
        s = Shared(f)
        self.assertTrue(s.matches(f))
        self.assertFalse(s.matches(self.test_shared_matcher))
        self.assertRegexpMatches(repr(s), re.compile(r"Shared[(]id: \d*[)]"))
        self.assertEqual(repr(Shared(1)), "Shared(1)")

        class A:
            def __repr__(self):
                raise Exception()
        self.assertRegexpMatches(repr(Shared(A())),
                                 re.compile(r"Shared[(]id: \d*[)]"))

    def test_sequence_matcher(self):
        s = Sequence(list, str)
        self.assertTrue(s.matches(["a", "b", "c"]))
        self.assertFalse(s.matches(["a", "b", 1]))
        self.assertFalse(s.matches(("a", "b")))
        self.assertEqual(repr(s), "Sequence(Matchtype(<class 'list'>)"
                         "(Matchtype(<class 'str'>)))")

    def test_mapping_matcher(self):
        s = Mapping(dict, str, int)
        self.assertTrue(s.matches({"a": 1, "b": 2, "c": 3}))
        self.assertFalse(s.matches({"a": 1, "b": 2, 1: 3}))
        self.assertFalse(s.matches(("a", "b")))
        self.assertFalse(s.matches({"a": 1, "b": 2, "c": "d"}))
        self.assertEqual(repr(s), "Mapping(Matchtype(<class 'dict'>)(Matchtype"
                         "(<class 'str'>): Matchtype(<class 'int'>)))")

    def test_any(self):
        a = Any()
        self.assertTrue(a.matches({"a": 1, "b": 2, "c": 3}))
        self.assertTrue(a.matches(["a", "b", "c"]))
        self.assertTrue(a.matches(False))
        self.assertEqual(repr(a), "Any()")

    def test_anyof(self):
        a = AnyOf((dict, list))
        self.assertTrue(a.matches({"a": 1, "b": 2, "c": 3}))
        self.assertTrue(a.matches(["a", "b", "c"]))
        self.assertFalse(a.matches({False, True}))
        self.assertEqual(repr(a), "AnyOf[Matchtype(<class 'dict'>), Matchtype("
                         "<class 'list'>)]")

    def test_allof(self):
        a = AllOf((dict, Any(), Mapping(dict, str, int)))
        self.assertTrue(a.matches({"a": 1, "b": 2, "c": 3}))
        self.assertFalse(a.matches({"a": 1, "b": 2, 1: 3}))
        self.assertFalse(a.matches(("a", "b")))
        self.assertFalse(a.matches({"a": 1, "b": 2, "c": "d"}))
        self.assertEqual(repr(a), "AllOf[Matchtype(<class 'dict'>), Any(), "
                         "Mapping(Matchtype(<class 'dict'>)(Matchtype(<class"
                         " 'str'>): Matchtype(<class 'int'>)))]")

if __name__ == "__main__":
    tv = TestVerify()
    tv.setUp()
    tv.test_verifyobj()
    tv.test_arg_checker()
    tv.test_arg_checker_ann()
