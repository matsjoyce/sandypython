from types import FunctionType

safe_names = {}
safe_modules = ()


def set_safe_modules(safe_mods):
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
    if module not in safe_modules:
        if safe:
            return
        raise ImportError("'%s' is restricted" % module)
    try:
        if obj:
            return getattr(__import__(module, None, None, [obj]), obj)
        else:
            return __import__(module)
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
