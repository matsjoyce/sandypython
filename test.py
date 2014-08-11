from sandypython import *
import sys
import os

sys.path.insert(0, "./badcode")


@verify.argschecker()
def prnt():
    with utils.DeactivateSandbox():
        import sys
        print(sys.version)
        print("Hello from free, unsecure, non-sandypythoned code!")
        print("getme.txt ==>", "'%s'" % open("getme.txt").read())


@verify.argschecker(__args__=verify.Sequence(tuple, verify.Any()), end=str, sep=str)
def printer(*args, **kwargs):
    s = " ".join([str(i) for i in args])
    kwargs["flush"] = True
    core.find_builtin("print")(s, **kwargs)


cols = {i: j for i, j in zip(("black", "red", "green", "yellow", "blue",
                              "magenta", "cyan", "white"), range(30, 38))}


@verify.argschecker(__args__=verify.Sequence(tuple, verify.Any()), color=str)
def colorfy(*args, color="green"):
    return "\033[1;{color}m{msg}\033[1;m".format(msg=" ".join(
        [str(i)for i in args]), color=cols[color])


@verify.argschecker(a=(int, dict, list, None), b=str, c=str)
def h(a, b, c=""):
    return str(a) + b + c


@verify.argschecker(s=verify.Any())
def loads(s):
    return safe_dill.loads(s)

core.add_default_builtins()

imp_map = {os.path.abspath("./badcode/*.py"): ["./badcode/*.py"],
           "<string>": ["./badcode/*.py"],
           "default": ["./badcode/*.py", "__sand__"]}
bad_code = open("badcode/bad_code%s.py" % sys.argv[1]).read()

core.add_to_exec_globals("prnt", prnt)
core.add_to_exec_globals("h", h)
core.add_to_exec_globals("colorfy", colorfy)
core.add_to_exec_globals("save", safe_dill.save)
core.add_to_exec_globals("load", safe_dill.load)
core.add_to_exec_globals("loads", loads)

imp_filter = importing.import_filter_by_path(imp_map)
safe_dill.set_safe_modules(imp_filter)
core.add_builtin("__import__", importing.checked_importer(imp_filter))
core.add_builtin("print", printer)
with utils.ActivateSandbox():
    core.exec_str(bad_code)
