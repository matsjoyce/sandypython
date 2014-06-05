import inspect
from . import core


imported_modules = set()
cols = {i: j for i, j in zip(("black", "red", "green", "yellow", "blue",
                              "magenta", "cyan", "white"), range(30, 38))}


def colorf(*args, color="green"):
    str_conv = []
    for i in args:
        try:
            str_conv.append(str(i))
        except:
            pass
    s = " ".join(str_conv)
    s = "\033[1;%dm%s\033[1;m" % (cols[color], s)
    return s


class DeactivateSandbox:
    def __enter__(self):
        core.end_sandbox()

    def __exit__(self, type, value, traceback):
        core.start_sandbox()


def check_builtins(func):
    def check_builtins_wrapper(*args, **kwargs):
        core.detamper_builtins()
        return func(*args, **kwargs)
    return check_builtins_wrapper


def get_type_name(t):
    if t is None:
        return "'None'"
    if isinstance(t, tuple):
        return (", ".join((get_type_name(i) for i in t[:-1]))
                + " or %s" % get_type_name(t[-1]))
    if not isinstance(t, type):
        t = type(t)
    if hasattr(t, "__name__"):
        return "'%s'" % t.__name__


def type_checker(**kwargs):
    def decorator(func):
        args_names = inspect.getargspec(func)[0]

        def type_checker_wrapper(*fargs, **fkwargs):
            core.detamper_builtins()
            for i, j in zip(fargs, args_names):
                fkwargs[j] = i

            for f, fv in fkwargs.items():
                t = kwargs[f]
                good = None
                if fv is None:
                    if t is None:
                        good = True
                    elif t.__class__ is tuple:
                        good = None in t
                elif t.__class__ is tuple:
                    good = type(fv) in t
                elif t.__class__ is type:
                    good = type(fv) is t
                if not good:
                    types = (f, get_type_name(t), get_type_name(fv))
                    raise TypeError("The argument for '%s' has to be a %s,"
                                    " not a %s" % types)

            return func(**fkwargs)

        type_checker_wrapper.__name__ = func.__name__
        type_checker_wrapper.__doc__ = func.__doc__
        return type_checker_wrapper
    return decorator


def clean_module(mod):
    if hasattr(mod, "__loader__"):
        del mod.__loader__
    if hasattr(mod, "__spec__"):
        del mod.__spec__
    mod.__builtins__ = __builtins__
    imported_modules.add(mod)


def allowed(name, fname, allowed_map):
    if name in allowed_map["default"]:
        return True
    for i in allowed_map:
        if fname.endswith(i) and i != "default":
            if name in allowed_map[i]:
                return True
    return False


def checked_importer(allowed_map, noise=False):
    import _frozen_importlib as froz_imp_lib

    @type_checker(name=str, globals=(dict, None), locals=(dict, None),
                  fromlist=(tuple, list, None), level=int)
    def controlled_importer(name, globals=None,
                            locals=None, fromlist=(), level=0):
        if name == core.env_name:
            return core.exec_mod

        with DeactivateSandbox():
            stack = inspect.stack()

        # get caller details. The index is 2 as we have 1 decorator
        (frame, fname, lineno, func_name, lines, index) = stack[2]

        if noise:
            print(colorf("Importing %s from file %s:%d: " %
                         (name, fname, lineno), color="blue"), end="")

        if allowed(name, fname, allowed_map) or fname == __file__:
            if noise:
                print(colorf("Allowed", color="blue"))

            # give the import mechanism the function that is needs
            froz_imp_lib.__dict__["exec"] = core.find_builtin("exec")
            froz_imp_lib.__dict__["compile"] = core.find_builtin("compile")

            mod = core.find_builtin("__import__")(name, globals, locals,
                                                  fromlist, level)

            # then take them away again
            froz_imp_lib.__dict__["exec"]
            froz_imp_lib.__dict__["compile"]

            clean_module(mod)
            return mod
        else:
            if noise:
                print(colorf("Denied", color="red"))
            raise ImportError("'%s' is restricted" % name)
    return controlled_importer
