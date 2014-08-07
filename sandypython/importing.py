import fnmatch
import inspect
import os
import sys
import types
from .utils import DeactivateSandbox, type_checker_annotated, colorf
from . import core


def import_filter_by_name(allowed_map):
    """
    Filter for :func:`checked_importer` which takes a dict of paths against
    allowed names. The "default" key represents the modules all code can
    import.

    Example::

        imp_map = {os.path.abspath("./badcode/*.py"): ["./badcode/*.py"],
                   "default": ["sys"]}
        i = import_filter_by_name(imp_map)
        i("sys", "random place", "doesn't matter")  # True
        i("a_mod", "random place", "doesn't matter")  # False
        i("a_mod", "./badcode/a_mod_importer.py", "doesn't matter")  # True
    """
    def filter(name, fname, module_path):
        if name in allowed_map["default"]:
            return True
        for i in allowed_map:
            if fnmatch.fnmatch(fname, i) and i != "default":
                if name in allowed_map[i]:
                    return True
        return False
    return filter


def import_filter_by_path(allowed_map):
    """
    Filter for :func:`checked_importer` which takes a dict of paths against
    allowed import paths. The "default" key represents the modules all code can
    import.

    Example::

        imp_map = {os.path.abspath("./*.py"): ["/*.py"],
                   "default": ["./*.py"]}
        i = import_filter_by_path(imp_map)
        i("sys", "random place", "/usr/lib/python3.4/sys.py")  # False
        i("a_mod", "random place", "./a_mod.py")  # True
        i("a_mod", "./a_mod_importer.py", "/usr/lib/python3.4/sys.py")  # True
    """
    def filter(name, fname, module_path):
        for path in allowed_map["default"]:
            if fnmatch.fnmatch(module_path, os.path.abspath(path)):
                return True
        for i in allowed_map:
            if fnmatch.fnmatch(fname, i):
                for path in allowed_map[i]:
                    if fnmatch.fnmatch(module_path, os.path.abspath(path)):
                        return True
        return False
    return filter


def do_import(filename, name, globals, locals, fromlist, level):
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    code = open(filename).read()
    exec(code, core.begin_globals, mod.__dict__)
    if fromlist:
        pass
    else:
        return mod


def checked_importer(imp_filter, noise=False):
    """
    :param imp_filter: function that should take the name of the module to
        import, the path of the code importing the module and the path to
        the module, and return a boolean indicating whether the import is
        allowed or not
    :type imp_filter: function
    :param noise: enables extra logging info
    :type noise: bool

    Importer that can be used to replace __import__.

    Example::

        core.replace_builtin("__import__", utils.checked_importer(imp_filter))
    """
    @type_checker_annotated
    def controlled_importer(name: str, globals: (dict, None)=None,
                            locals: (dict, None)=None,
                            fromlist: (tuple, list, None)=(), level: int=0):
        if name == core.env_name:
            return core.exec_mod

        with DeactivateSandbox():
            stack = inspect.stack()

        # get caller details. The index is 2 as we have 1 decorator
        (frame, fname, lineno, func_name, lines, index) = stack[2]

        if noise:
            print(colorf("Importing %s from file %s:%d: " %
                         (name, fname, lineno), color="blue"), end="")

        module_path = ""
        for path in sys.path:
            for hook in sys.path_hooks:
                try:
                    loader = hook(path).find_module(name)
                    if loader:
                        module_path = loader.path
                        break
                except ImportError:
                    pass
        module_path = os.path.abspath(module_path) if module_path else ""

        if imp_filter(name, fname, module_path) or fname == __file__:
            if noise:
                print(colorf("Allowed", color="blue"))

            mod = do_import(module_path, name, globals, locals, fromlist, level)

            return mod
        else:
            if noise:
                print(colorf("Denied", color="red"))
            raise ImportError("'%s' is restricted" % name)
    return controlled_importer
