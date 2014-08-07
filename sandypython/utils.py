import inspect
from . import core, spec

__all__ = ["DeactivateSandbox", "ActivateSandbox", "check_builtins",
           "type_checker", "type_checker_annotated", "Any", "checked_importer",
           "import_filter_by_name", "import_filter_by_path"]

imported_modules = set()
cols = {i: j for i, j in zip(("black", "red", "green", "yellow", "blue",
                              "magenta", "cyan", "white"), range(30, 38))}


def colorf(*args, color="green"):
    s = " ".join([str(i) for i in args])
    s = "\033[1;%dm%s\033[1;m" % (cols[color], s)
    return s


class DeactivateSandbox:
    """
    Context manager which will call :func:`sandypython.core.end_sandbox`
    if the sandbox was started, then :func:`sandypython.core.start_sandbox`
    if it ended it. It is save to use this without activating the sandbox
    before hand (it will be a no-op).

    Example::

        with utils.DeactivateSandbox:
            open("f.txt")
            import sys

    """
    def __enter__(self):
        self.reinit = core.started
        core.end_sandbox()
        return self

    def __exit__(self, type, value, traceback):
        if self.reinit:
            core.start_sandbox()


class ActivateSandbox:
    """
    Context manager which will call :func:`sandypython.core.start_sandbox`
    if the sandbox has not been started, then
    :func:`sandypython.core.end_sandbox` if it started it. It is save to
    use this with the sandbox already started (it will be a no-op).

    Example::

        with utils.ActivateSandbox:
            core.exec_str(bad_code)

    """
    def __enter__(self):
        self.end = not core.started
        core.start_sandbox()
        return self

    def __exit__(self, type, value, traceback):
        if self.end:
            core.end_sandbox()


def check_builtins(func):
    """
    A decorator to make sure :func:`sandypython.core.detamper_builtins` is
    called before any function code
    """
    def check_builtins_wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    check_builtins_wrapper.__name__ = func.__name__
    check_builtins_wrapper.__doc__ = func.__doc__
    return check_builtins_wrapper


def get_type_name(t):
    if t is None:
        return "'None'"
    if isinstance(t, tuple):
        return (", ".join((get_type_name(i) for i in t[:-1]))
                + " or %s" % get_type_name(t[-1]))
    if not isinstance(t, type):
        t = type(t)
    return "'%s'" % t.__name__


class Any:
    """
    Placeholder class used by :func:`type_checker` and
    :func:`type_checker_annotated` to represent any type.
    """
    pass


def check(fv, t):
    if fv is None:
        if t is None:
            return True
        return spec.getsattr(t, "__class__") is tuple and None in t
    elif spec.getsattr(t, "__class__") is tuple:
        return type(fv) in t
    return spec.getsattr(t, "__class__") is type and type(fv) is t


def type_checker(**kwargs):
    """
    Checks the types of all arguments against what is expected, and raises
    :class:`TypeError` if they do not. It can be used to ensure no malicious
    types can enter a function that lifts the sandbox. It takes the types in
    kwarg form. A tuple of types means that the args can be any of those in
    the tuple. :class:`Any` can be used to indicate any type.

    Example::

        @type_checker(self=Any, a=(int, dict, None), b=str, c=str)
        def f(self, a, b, c=""):
            return str(a) + b + c
    """
    from .spec import getsattr

    def decorator(func):
        args_names = inspect.getargspec(func)[0]

        def type_checker_wrapper(*fargs, **fkwargs):
            for i, j in zip(fargs, args_names):
                fkwargs[j] = i

            for f, fv in fkwargs.items():
                t = kwargs[f]
                if t is Any:
                    continue
                if not check(fv, t):
                    types = (f, get_type_name(t), get_type_name(fv))
                    raise TypeError("The argument for '%s' has to be a %s,"
                                    " not a %s" % types)

            return func(**fkwargs)

        type_checker_wrapper.__name__ = func.__name__
        type_checker_wrapper.__doc__ = func.__doc__
        return type_checker_wrapper
    return decorator


def type_checker_annotated(func):
    """
    Same usage as :func:`type_checker`, but takes the types in annotation form.

    Example::

        @type_checker_annotated
        def f_ann(self: Any, a: (int, dict, list, None), b: str, c: str=""):
            return str(a) + b + c
    """
    args_names = inspect.getfullargspec(func)[0]
    annotations = func.__annotations__

    def type_checker_wrapper(*fargs, **fkwargs):
        for i, j in zip(fargs, args_names):
            fkwargs[j] = i

        for f, fv in fkwargs.items():
            t = annotations[f]
            if t is Any:
                continue
            if not check(fv, t):
                types = (f, get_type_name(t), get_type_name(fv))
                raise TypeError("The argument for '%s' has to be a %s,"
                                " not a %s" % types)

        return func(**fkwargs)

    type_checker_wrapper.__name__ = func.__name__
    type_checker_wrapper.__doc__ = func.__doc__
    return type_checker_wrapper
