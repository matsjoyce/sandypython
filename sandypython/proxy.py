import copy

noproxy = {None, True, False, NotImplemented, ..., ArithmeticError,
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
           staticmethod, classmethod, frozenset}

noproxytypes = {str, int, bool, range, type(any), bytearray, float,
                bytes, object, complex}
proxies = {}
made_proxies = {}


def return_whole(obj):
    try:
        return obj in noproxy or obj in noproxytypes or type(obj) in noproxytypes
    except:
        return False


def make_proxy(obj):
    if id(obj) in made_proxies:
        if obj is made_proxies[id(obj)][0]:
            return made_proxies[id(obj)][1]
    elif return_whole(obj):
        made_proxies[id(obj)] = obj, obj
        return obj
    elif type(obj) in proxies:
        p = proxies[type(obj)](obj)
        made_proxies[id(obj)] = obj, p
        return p
    else:
        return copy.deepcopy(obj)


def add_to_proxies(type, func=None):
    if func:
        proxies[type] = func
    else:  # decorator
        def wrap(func):
            proxies[type] = func
            return func
        return wrap


@add_to_proxies(type)
def class_proxy(obj):
    return type(obj.__name__, (obj,), {})


@add_to_proxies(type(make_proxy))
def func_proxy(obj):
    def proxy(*args, **kwargs):
        try:
            return obj(*args, **kwargs)
        except BaseException as e:
            if type(e) in noproxytypes:
                raise e
            else:
                new_e_type = make_proxy(type(e))
                new_e = new_e_type.__new__(new_e_type)
                new_e.__dict__ = e.__dict__
                raise new_e
    return proxy
