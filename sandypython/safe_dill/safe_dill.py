from types import FunctionType
from .. import core, importing
import sys
import os

safe_names = {}
safe_modules = None

sandy_func_list = {}


def retrive_sf(name_):
    for name, obj in sandy_func_list.values():
        if name == name_:
            return obj


def scan(name, obj, seen, lst):
    if id(obj) in seen:
        return
    elif not isinstance(obj, (int, str)):
        if id(obj) not in lst:
            lst[id(obj)] = name, obj

    if hasattr(obj, "__dict__"):
        for name2, obj2 in obj.__dict__.items():
            scan(name + "." + name2, obj2, seen, lst)
    if hasattr(obj, "items"):
        try:
            for k, v in obj.items():
                scan(name + "[{!r}]".format(k), v, seen, lst)
        except:
            pass
    else:
        try:
            for i, v in enumerate(obj.items()):
                scan(name + "[{}]".format(i), v, seen, lst)
        except:
            pass


def make_sandy_func_list(force=False):
    global sandy_func_list
    if not sandy_func_list or force:
        seen = set()
        lst = {}
        for name, obj in core.begin_globals.items():
            scan(name, obj, seen, lst)
        sandy_func_list = lst


def set_safe_modules(safe_mods):
    """
    Set a list of safe modules that pickle's load global opcode can import.
    """
    global safe_modules
    safe_modules = safe_mods


def _import_module(import_name, safe=False):
    if import_name in safe_names:
        return safe_names[import_name]
    if "." in import_name:
        items = import_name.split(".")
        module = ".".join(items[:-1])
        obj = items[-1]
    else:
        module = import_name
        obj = ""

    module_path = ""
    for path in sys.path:
        for hook in sys.path_hooks:
            try:
                loader = hook(path).find_module(module)
                if loader:
                    module_path = loader.path
                    break
            except ImportError:
                pass

    if not safe_modules or not safe_modules(module, __file__,
                                            os.path.abspath(module_path)):
        if safe:
            return
        raise ImportError("'%s' is restricted" % module)
    try:
        if obj:
            return getattr(importing.do_import(module_path, module, None,
                                               None, [obj]), obj)
        else:
            return importing.do_import(module_path, module)
    except (ImportError, AttributeError):
        if not safe:
            raise

_import_module.__module__ = "sandypython.safe_dill.dill"
safe_names["sandypython.safe_dill.dill._import_module"] = _import_module


def init():
    from . import dill

    dill._import_module = _import_module
    safe_names["sandypython.safe_dill.dill._unmarshal"] = dill._unmarshal
    safe_names["sandypython.safe_dill.dill._create_function"] = \
        dill._create_function
    safe_names["sandypython.safe_dill.dill._create_cell"] = dill._create_cell
    safe_names["sandypython.safe_dill.dill._eval_repr"] = dill._eval_repr
    safe_names["sandypython.safe_dill.dill._load_type"] = dill._load_type
    safe_names["sandypython.safe_dill.dill._get_attr"] = dill._get_attr
    safe_names["sandypython.safe_dill.safe_dill.retrive_sf"] = retrive_sf
