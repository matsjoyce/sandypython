import sandbox
from . import pickle, dill
from .safe_dill import safe_modules


@sandbox.check_builtins
def save():
    with sandbox.find_builtin("open")("/tmp/sand.pkl", "wb") as f:
        pickler = dill.Pickler(f, 4)
        pickler._main_module = sandbox.core.exec_mod
        pickler._byref = False
        pickler._session = False

        exec_globs_cpy = sandbox.core.exec_globals.copy()
        a = set(list(sandbox.core.exec_globals.keys()))
        sandbox.core.exec_globals.pop("__builtins__")
        sandbox.core.exec_globals.pop("__sand__")
        for i in sandbox.core.added_to_execgs:
            sandbox.core.exec_globals.pop(i)

        pickler.dump(sandbox.core.exec_globals)

        sandbox.core.exec_globals.update(exec_globs_cpy)


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


@sandbox.check_builtins
def load():
    with sandbox.find_builtin("open")("/tmp/sand.pkl", "rb") as f:
        unpickler = HackedUnpickler(sandbox.core.exec_globals, f)
        unpickler._main_module = sandbox.core.exec_mod
        unpickler._session = False

        exec_globs = unpickler.load()

        sandbox.core.exec_globals.update(exec_globs)
