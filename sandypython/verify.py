from abc import ABCMeta, abstractmethod
from .spec import getsattr
import types
import inspect

__all__ = ["Matcher", "Matchtype", "Shared", "Sequence", "Mapping", "Any",
           "AnyOf", "AllOf", "setinstverify", "settypeverify", "setargsverify",
           "argschecker", "argschecker_ann", "verifyobj", "verifyargs",
           "generateinstverify", "generatetypeverify"]

func_args_ver = {}  # dict of function to signature data

# dict of type to verification data
# verification data is a dict of member to type, shared or sequence

type_ver = {}  # type
type_nover = {type(None), True, False, NotImplemented, ..., ArithmeticError,
              AssertionError, AttributeError,
              BaseException, BlockingIOError, BrokenPipeError,
              BufferError, BytesWarning, ChildProcessError,
              ConnectionAbortedError, ConnectionError,
              ConnectionRefusedError, ConnectionResetError,
              DeprecationWarning, EOFError,
              EnvironmentError, Exception, FileExistsError,
              FileNotFoundError, FloatingPointError, FutureWarning,
              GeneratorExit, IOError, ImportError, ImportWarning,
              IndentationError, IndexError, InterruptedError,
              IsADirectoryError, KeyError, KeyboardInterrupt,
              LookupError, MemoryError, NameError,
              NotADirectoryError, NotImplementedError,
              OSError, OverflowError, PendingDeprecationWarning,
              PermissionError, ProcessLookupError, ReferenceError,
              ResourceWarning, RuntimeError, RuntimeWarning,
              StopIteration, SyntaxError, SyntaxWarning,
              SystemError, SystemExit, TabError, TimeoutError,
              TypeError, UnboundLocalError,
              UnicodeDecodeError, UnicodeEncodeError, UnicodeError,
              UnicodeTranslateError, UnicodeWarning, UserWarning,
              ValueError, Warning, ZeroDivisionError, list, dict, set, map,
              property, slice, enumerate, tuple, super, filter, reversed, zip,
              staticmethod, classmethod, frozenset, str, int, bool, range,
              types.BuiltinFunctionType, bytearray, float, bytes, object,
              complex, types.FunctionType, types.GetSetDescriptorType,
              types.CodeType, types.ModuleType}

inst_ver = {}  # instance
inst_nover = {str, int, bool, range, type(any), bytearray, float,
              bytes, object, complex, None, True, False, NotImplemented, ...,
              types.GetSetDescriptorType, type(None), types.CodeType, dict,
              list, tuple, types.ModuleType}

noise = False


def debug():
    global noise
    noise = True


def printer(*args, **kwargs):
    if noise:
        return print(*args, **kwargs)


def check_matcher(matcher):
    if isinstance(matcher, Matcher):
        return matcher
    elif isinstance(matcher, tuple):
        return AnyOf(matcher)
    elif matcher in (None, type(None)):
        return Shared(None)
    else:
        return Matchtype(matcher)


class Matcher(metaclass=ABCMeta):
    """
    Base class for matchers. You should inherit from this when creating
    custom matchers.

    Example::

        class MyMatcher(Matcher):
            def matches(self, obj):
                return obj == magic_global_obj

            def __repr__(self):
                return "{}()".format(self.__class__.__name__)
    """
    @abstractmethod
    def matches(self, obj) -> bool:
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Matchtype(Matcher):
    """
    Matcher which returns True when type(obj) == type given in constructer.

    Example::

        m = Matchtype(str)
        m.matches("a")  # True
        m.matches(1)  # False

    Shortcut: `settypeverify(A, a=str)` is equivelent to
    `settypeverify(A, a=Matchtype(str))`
    """
    def __init__(self, type_):
        assert isinstance(type_, type)
        self.type = type_

    def matches(self, obj):
        if obj is None:
            return self.type is None
        return getsattr(self.type, "__class__") is type \
            and type(obj) is self.type

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.type)


class Shared(Matcher):
    """
    Matcher which returns True when obj == obj given in constructer.

    Example::

        def f():
            pass
        m = Shared(f)
        m.matches(f)  # True
        m.matches(g)  # False
    """
    def __init__(self, obj):
        self.obj = obj

    def matches(self, obj):
        printer(id(self.obj), id(obj), self.obj, obj)
        return obj is self.obj

    def __repr__(self):
        try:
            r = repr(self.obj)
        except:
            r = ""
        if r == "" or len(r) > 30:
            r = "id: {}".format(id(self.obj))

        return "{}({})".format(self.__class__.__name__, r)


class Sequence(Matchtype):
    """
    Matcher which returns True when a sequence type matches `type_matcher`
    and all the items match `item_matcher`.

    Example::

        s = Sequence(list, str)
        s.matches(["a", "b", "c"])  # True
        s.matches(["a", "b", 1])  # False
        s.matches(("a", "b"))  # False
    """
    def __init__(self, type_matcher, item_matcher):
        self.type_matcher = check_matcher(type_matcher)
        self.item_matcher = check_matcher(item_matcher)

    def matches(self, obj):
        if not self.type_matcher.matches(obj):
            return False
        for i in obj:
            if not self.item_matcher.matches(i):
                return False
        return True

    def __repr__(self):
        return "{}({}({}))".format(self.__class__.__name__, self.type_matcher,
                                   self.item_matcher)


class Mapping(Matchtype):
    """
    Matcher which returns True when a sequence type matches `type_matcher`
    and all the keys match `key_matcher` and the values match `value_matcher`.

    Example::

        s = Mapping(dict, str, int)
        s.matches({"a": 1, "b": 2, "c": 3})  # True
        s.matches({"a": 1, "b": 2, 1: 3})  # False
        s.matches(("a", "b"))  # False
        s.matches({"a": 1, "b": 2, "c": "d"})  # False
    """
    def __init__(self, type_matcher, key_matcher, value_matcher):
        self.type_matcher = check_matcher(type_matcher)
        self.key_matcher = check_matcher(key_matcher)
        self.value_matcher = check_matcher(value_matcher)

    def matches(self, obj):
        if not self.type_matcher.matches(obj):
            return False
        for key, val in obj.items():
            if not (self.key_matcher.matches(key)
               and self.value_matcher.matches(val)):
                return False
        return True

    def __repr__(self):
        return "{}({}({}: {}))".format(self.__class__.__name__,
                                       self.type_matcher, self.key_matcher,
                                       self.value_matcher)


class Any(Matcher):
    """
    Matcher which returns True for anything.

    Example::

        a = Any()
        a.matches({"a": 1, "b": 2, "c": 3})  # True
        a.matches(["a", "b", "c"])  # True
        a.matches(False)  # True
    """
    def matches(self, obj):
        return True

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class AnyOf(Matcher):
    """
    Matcher which returns True if any of the matchers given in the
    constructed match.

    Example::

        a = AnyOf((dict, list))
        a.matches({"a": 1, "b": 2, "c": 3})  # True
        a.matches(["a", "b", "c"])  # True
        a.matches({False, True})  # False

    Shortcut: A tuple of matchers is equivalent to this type
    """
    def __init__(self, matchers):
        self.matchers = [check_matcher(m) for m in matchers]

    def matches(self, obj):
        return any(m.matches(obj) for m in self.matchers)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.matchers)


class AllOf(Matcher):
    """
    Matcher which returns True if all of the matchers given in the
    constructed match.

    Example::

        a = AllOf((dict, Any(), Mapping(dict, str, int)))
        a.matches({"a": 1, "b": 2, "c": 3})  # True
        a.matches({"a": 1, "b": 2, 1: 3})  # False
        a.matches(("a", "b"))  # False
        a.matches({"a": 1, "b": 2, "c": "d"})  # False
    """
    def __init__(self, matchers):
        self.matchers = [check_matcher(m) for m in matchers]

    def matches(self, obj):
        return all(m.matches(obj) for m in self.matchers)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.matchers)


def setinstverify(type, **verify_data):
    """
    Adds verification data for an instance of type for later use by
    :func:`verifyobj`.

    Example::

        setinstverify(WierdObj, __weakref__=None, a=str, b=(int, dict))
    """
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    inst_ver[type] = verify_data


def settypeverify(type, **verify_data):
    """
    Adds verification data for a type for later use by :func:`verifyobj`.

    Example::

        settypeverify(WierdObj, a=int, __module__=str, __doc__=(None, str),
                      __init__=Shared(WierdObj.__init__),
                      __weakref__=Shared(WierdObj.__weakref__),
                      __dict__=Shared(WierdObj.__dict__))
    """
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    type_ver[type] = verify_data


def setargsverify(func, **verify_data):
    """
    Adds verification data for a function's args for later use by
    :func:`verifyargs`. This function is best used though
    :func:`argschecker` or :func:`argschecker_ann`
    """
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    func_args_ver[func] = verify_data

checked_func_names = ("arg_checked_func", "check_builtins_wrapper",
                      "type_checker_wrapper")


def argschecker(**verify_data):
    """
    Checks the types of all arguments against what is expected, and raises
    :class:`RuntimeError` if they do not. It can be used to ensure no malicious
    types can enter a function that lifts the sandbox. It takes the matchers in
    kwarg form. `__args__` can be used to check `*args` and `__kwargs__` can be
    used to check `**kwargs`.

    Example::

        @argschecker(self=Any(), a=(int, dict, None), b=str, c=str,
            __args__=Sequence(tuple, str))
        def f(self, a, b, *args, c=""):
            return str(a) + b + c
    """
    def savkw(func):
        setargsverify(func, **verify_data)
        args_names = inspect.getfullargspec(func)[0]

        def arg_checked_func(*args, **kwargs):
            for i, j in zip(args, args_names):
                kwargs[j] = i
            kwargs_cpy = kwargs.copy()
            if len(args) > len(args_names):
                args = kwargs_cpy["__args__"] = tuple(args[len(args_names):])
            else:
                args = ()

            v = verifyargs(func, kwargs_cpy)
            if v:
                raise RuntimeError("Argument verification"
                                   " of arg '{1}' failed: {0}".format(*v))
            from . import core
            for i, j in core.exec_globals.items():
                if type(i) is not str:
                    raise RuntimeError("Argument verification"
                                       " of global '{1}' failed: {0}"
                                       .format(*v))
                v = verifyobj(j)
                if v:
                    raise RuntimeError("Argument verification"
                                       " of global '{1}' failed: {0}"
                                       .format(*v))

            return func(*args, **kwargs)
        return arg_checked_func
    return savkw


def argschecker_ann(func):
    """
    Same usage as :func:`argschecker`, but takes the types in annotation form.

    Example::

        @argschecker_ann
        def f_ann(self: Any(), a: (int, dict, list, None), b: str,
           *__args__: Sequence(tuple, str), c: str=""):
            return str(a) + b + c
    """
    setargsverify(func, **func.__annotations__)
    args_names = inspect.getfullargspec(func)[0]

    def arg_checked_func(*args, **kwargs):
        for i, j in zip(args, args_names):
            kwargs[j] = i
        kwargs_cpy = kwargs.copy()
        if len(args) > len(args_names):
            args = kwargs_cpy["__args__"] = tuple(args[len(args_names):])
        else:
            args = ()

        v = verifyargs(func, kwargs_cpy)
        if v:
            raise RuntimeError("Argument verification"
                               " of arg '{1}' failed: {0}".format(*v))

        return func(*args, **kwargs)
    return arg_checked_func


def verifyinst(obj):
    if type(obj) in inst_nover:
        return
    assert type(obj) is not type
    inst_verify_data = inst_ver[type(obj)]
    # check instance
    for key, item in getsattr(obj, "__dict__").items():
        if type(key) is not str:
            return "key in __dict__ is not of type str but {}{}".format(
                type(key), type(key) == str), obj
        if key in inst_verify_data:
            if not inst_verify_data[key].matches(item):
                return "key '{}' has failed verification".format(key), obj
            v = verifyobj(item)
            if v:
                return v
        else:
            return "key '{}' not in verify data".format(key), obj
    # check getset_descriptors, good for things like functions
    for key, item in getsattr(type(obj), "__dict__").items():
        if key == "__dict__":
            continue
        if type(item) in (types.GetSetDescriptorType,
                          types.MemberDescriptorType):
            item = getsattr(item, "__get__")(obj)
            if key in inst_verify_data:
                if not inst_verify_data[key].matches(item):
                    return "key '{}' has failed verification".format(key), obj
                v = verifyobj(item)
                if v:
                    return v
            else:
                return "key '{}' not in verify data".format(key), obj


def verifytype(typ):
    if typ in type_nover:
        return
    type_verify_data = type_ver[typ]
    # check instance
    for key, item in getsattr(typ, "__dict__").items():
        if key == "__dict__":
            continue
        if type(key) is not str:
            return "key in __dict__ is not of type str", typ
        if type(item) in (types.GetSetDescriptorType,
                          types.MemberDescriptorType):
            continue
        if key in type_verify_data:
            if not type_verify_data[key].matches(item):
                return "key '{}' has failed verification".format(key), typ
            v = verifyobj(item)
            if v:
                return v
        else:
            return "key '{}' not in verify data".format(key), typ
    print(dir(typ))
    for base in getsattr(typ, "__bases__"):
        v = verifytype(base)
        if v:
            return v


def verifyobj(obj):
    """
    Verifies obj using verification information stored by :func:`setinstverify`
    and :func:`settypeverify`. Returns None if the object is OK, otherwise
    returns a tuple of (reason, subojb) where subobj is the attr of obj that
    failed.
    """
    printer("Verifing", obj, type(obj))
    if type(obj) is type:
        return verifytype(obj)
    else:
        return verifyinst(obj) or verifytype(type(obj))


def verifyargs(func, args):
    """
    Verifies the args using verification information stored by
    :func:`setargsverify`. This function is best used though
    :func:`argschecker` or :func:`argschecker_ann`
    """
    assert isinstance(args, dict)
    verdat = func_args_ver[func]
    for key, value in args.items():
        if type(key) is not str:
            return "key in args is not of type str", key
        if key in verdat:
            if not verdat[key].matches(value):
                return "key '{}' has failed verification".format(key), key
            v = verifyobj(value)
            if v:
                return v, key
        else:
            if "__kwargs__" in verdat:
                if not verdat["__kwargs__"].matches(value):
                    return "key '{}' has failed verification".format(key), key
                v = verifyobj(value)
                if v:
                    return v, key
            else:
                return "key '{}' not in verify data".format(key), key


def generatetypeverify(typ):
    """
    Attempts to generate and set data for :func:`verifyobj`. If the type
    can change (e.g. class variables that can change), it is best to use
    :func:`settypeverify`.
    """
    vd = {}
    for key, value in getsattr(typ, "__dict__").items():
        vd[key] = Shared(value)
    settypeverify(typ, **vd)
    return vd


def generateinstverify(example):
    """
    Attempts to generate and set data for :func:`verifyobj`. If the instance
    is not simple, it is best to use :func:`setinstverify`.
    """
    vd = {}
    for key, value in getsattr(example, "__dict__").items():
        vd[key] = check_matcher(type(value))
    for key, value in getsattr(type(example), "__dict__").items():
        if type(value) in (types.GetSetDescriptorType,
                           types.MemberDescriptorType):
            vd[key] = check_matcher(type(getsattr(value, "__get__")(example)))
    setinstverify(type(example), **vd)
    return vd


dictstrany = Mapping(dict, str, Any())

setinstverify(types.FunctionType, __name__=str, __module__=str,
              __qualname__=str, __code__=types.CodeType,
              __kwdefaults__=(dictstrany, None),
              __annotations__=dictstrany, __defaults__=(dictstrany, None),
              __doc__=(str, None), __closure__=(tuple, None),
              __globals__=dictstrany)
