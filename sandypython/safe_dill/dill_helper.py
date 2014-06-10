from .. import core
from ..utils import check_builtins
from ..spec import getsattr
from . import pickle, dill
from .safe_dill import safe_modules

old_getsattr = dill.getsattr


@check_builtins
def save(filename="/tmp/sand.pkl"):
    """
    Save the contents of the sandbox's globals, to be restored by :func:`load`.
    """
    with core.find_builtin("open")(filename, "wb") as f:
        pickler = dill.Pickler(f, 4)
        pickler._main_module = core.exec_mod
        pickler._byref = False
        pickler._session = False

        exec_globs_cpy = core.exec_globals.copy()
        a = set(list(core.exec_globals.keys()))
        core.exec_globals.pop("__builtins__")
        core.exec_globals.pop("__sand__")
        for i in core.added_to_execgs:
            core.exec_globals.pop(i)

        pickler.dump(core.exec_globals)

        core.exec_globals.update(exec_globs_cpy)


class HackedUnpickler(pickle._Unpickler):
    def __init__(self, start_dict, *args, **kwargs):
        self.start_dict = start_dict
        super().__init__(*args, **kwargs)

    def load_empty_dictionary(self):
        if self.start_dict is not None:
            self.append(self.start_dict)
            self.start_dict = None
        else:
            self.append({})
    pickle._Unpickler.dispatch[pickle.EMPTY_DICT[0]] = load_empty_dictionary


@check_builtins
def load(filename="/tmp/sand.pkl"):
    """
    Load the contents of the sandbox's globals which has been saved by
    :func:`save`.
    """
    with core.find_builtin("open")(filename, "rb") as f:
        unpickler = HackedUnpickler(core.exec_globals, f)
        unpickler._main_module = core.exec_mod
        unpickler._session = False

        exec_globs = unpickler.load()

        core.exec_globals.update(exec_globs)


def set_getsattr():
    dill.getsattr = getsattr


def unset_getsattr():
    dill.getsattr = old_getsattr
