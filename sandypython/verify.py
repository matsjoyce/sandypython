from abc import ABCMeta, abstractmethod
from .spec import getsattr
import types
import inspect

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
              types.CodeType}

inst_ver = {}  # instance
inst_nover = {str, int, bool, range, type(any), bytearray, float,
              bytes, object, complex, None, True, False, NotImplemented, ...,
              types.GetSetDescriptorType, type(None), types.CodeType, dict,
              list, tuple}

noise = False


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
    @abstractmethod
    def matches(self, obj) -> bool:
        pass

    @abstractmethod
    def __repr__(self):
        pass


class Matchtype(Matcher):
    def __init__(self, type):
        self.type = type

    def matches(self, obj):
        if obj is None:
            if self.type is None:
                return True
            return getsattr(self.type, "__class__") is tuple \
                and None in self.type
        elif getsattr(self.type, "__class__") is tuple:
            return type(obj) in self.type
        return getsattr(self.type, "__class__") is type \
            and type(obj) is self.type

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.type)


class Shared(Matcher):
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
    def __init__(self, type, item_matcher):
        super().__init__(type)
        self.item_matcher = check_matcher(item_matcher)

    def matches(self, obj):
        if not super().matches(obj):
            return False
        for i in obj:
            if not self.item_matcher.matches(i):
                return False
        return True


class Mapping(Matchtype):
    def __init__(self, type, key_matcher, value_matcher):
        self.type = type
        self.key_matcher = check_matcher(key_matcher)
        self.value_matcher = check_matcher(value_matcher)

    def matches(self, obj):
        if not super().matches(obj):
            return False
        for key, val in obj.items():
            if not (self.key_matcher.matches(key)
               or self.value_matcher.matches(val)):
                return False
        return True


class Any(Matcher):
    def matches(self, obj):
        return True

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


class AnyOf(Matcher):
    def __init__(self, matchers):
        self.matchers = [check_matcher(m) for m in matchers]

    def matches(self, obj):
        return any(m.matches(obj) for m in self.matchers)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.matchers)


class AllOf(Matcher):
    def __init__(self, matchers):
        self.matchers = [check_matcher(m) for m in matchers]

    def matches(self, obj):
        return all(m.matches(obj) for m in self.matchers)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.matchers)


def setinstverify(type, **verify_data):
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    inst_ver[type] = verify_data


def settypeverify(type, **verify_data):
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    type_ver[type] = verify_data


def setargsverify(func, **verify_data):
    verify_data = {key: check_matcher(matcher)
                   for key, matcher in verify_data.items()}
    func_args_ver[func] = verify_data

checked_func_names = "arg_checked_func", "check_builtins_wrapper", "type_checker_wrapper"


def argschecker(**verify_data):
    def savkw(func):
        setargsverify(func, **verify_data)
        args_names = inspect.getfullargspec(func)[0]

        def arg_checked_func(*args, **kwargs):
            for i, j in zip(args, args_names):
                kwargs[j] = i

            v = verifyargs(func, kwargs)
            if v:
                raise RuntimeError("Argument verification"
                                   " of arg '{1}' failed: {0}".format(*v))

            return func(**kwargs)
        return arg_checked_func
    return savkw


def verifyinst(obj):
    if type(obj) in inst_nover:
        return
    assert type(obj) is not type
    inst_verify_data = inst_ver[type(obj)]
    # check instance
    for key, item in obj.__dict__.items():
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
    for key, item in type(obj).__dict__.items():
        if key == "__dict__":
            continue
        if type(item) in (types.GetSetDescriptorType,
                          types.MemberDescriptorType):
            item = item.__get__(obj)
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
    for key, item in typ.__dict__.items():
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
    for base in typ.__bases__:
        v = verifytype(base)
        if v:
            return v


def verifyobj(obj):
    printer("Verifing", obj, type(obj))
    if type(obj) is type:
        return verifytype(obj)
    else:
        return verifyinst(obj) or verifytype(type(obj))


def verifyargs(func, args):
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
            return "key '{}' not in verify data".format(key), key


def generatetypeverify(typ):
    vd = {}
    for key, value in typ.__dict__.items():
        vd[key] = Shared(value)
    settypeverify(typ, **vd)
    return vd


def generateinstverify(example):
    vd = {}
    for key, value in example.__dict__.items():
        vd[key] = check_matcher(type(value))
    for key, value in type(example).__dict__.items():
        if type(value) in (types.GetSetDescriptorType,
                           types.MemberDescriptorType):
            vd[key] = check_matcher(type(value.__get__(example)))
    setinstverify(type(example), **vd)
    return vd


dictstrany = Mapping(dict, str, Any())

setinstverify(types.FunctionType, __name__=str, __module__=str,
              __qualname__=str, __code__=types.CodeType,
              __kwdefaults__=(dictstrany, None),
              __annotations__=dictstrany, __defaults__=(dictstrany, None),
              __doc__=(str, None), __closure__=(tuple, None),
              __globals__=dictstrany)
