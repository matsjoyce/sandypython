def try_to_get_round_type_guard():
    h(0, "", "")  # should work
    try:
        h(0, 0, "")
        return True
    except Exception as e:
        pass
    try:
        class str(__builtins__["str"]):
            pass
        __builtins__["str"] = str
        h(0, str(), "hi")
        return True
    except Exception as e:
        pass
    h(c="hoo", a=0, b="boo")  # should work
    h(0, b="mushroom", c="crumple")  # should work
    try:
        h("", b="bear", c="sandbag")
        return True
    except Exception as e:
        pass
    h({}, b="box", c=" of sand")  # should work


def try_to_import_modules():
    import a_mod
    a_mod.a = 1
    try:
        import sys
    except ImportError as e:
        return False
    else:
        return True


doing = False


# Adapted from nedbatchelder.com/blog/201302/finding_python_3_builtins.html
def try_to_find_builtins():
    def f(func):
        def w(*args):
            return func(*args)
        return w

    @f
    def f2():
        pass

    wanted_funcs = ("open", "__import__", "exec", "compile", "system",
                    "print", "quit", "eval", "code", "end_sandbox")
    unwanted_modules = ("builtins", __name__, None, "sandypython.fakemod",
                        "sandypython.utils", "sandypython.proxy", "copyreg",
                        "a_mod", "__main__", "bad_module")
    constructer_args = [(), (4), (1), ("x",), ("x", "y"), ("x", "y", "z"),
                        ("utf8",), ("os",), ("sys",), ("io",), (1, 2, 3),
                        (0, 0, 0, 0, 0, b"KABOOM", (), (), (), "", "", 0, b""),
                        ("io",), ("a_mod",), ("functools",), (lambda x:x, ),
                        ({},), ([],), (f,), (f2,), ("__builtins__",),
                        ("builtins",), ("dill",), ("dill.dill",),
                        (b"\x80\x03cdill.dill\n_import_module\nq\x00X\x04\x00"
                         b"\x00\x00dillq\x01X\x00\x00\x00\x00q\x02\x86q\x03Rq"
                         b"\x04.",),
                        (b"\x80\x03cdill.dill\nsys\nq\x00.",),
                        (b"\x80\x03csys\nmodules\nq\x00.",),
                        ]
    constructer_args += [(i,) for i in wanted_funcs]

    global doing
    if doing:  # stop infinite recursion
        return
    max_depth = 400
    doing = True
    found = [0]

    def is_builtins(v):
        if type(v) == dict and "__name__" in v and v["__name__"] == "__builtins__":
            return "__builtins__"
        if hasattr(v, "__name__"):
            if v.__name__ in wanted_funcs:
                if v.__name__ == "code" and \
                        type(v).__name__ == "member_descriptor":
                    pass
                else:
                    return "v.__name__ = {}".format(v.__name__)
            if "IO" in v.__name__ and "Error" not in v.__name__:
                    return "IO in v"
        if hasattr(v, "__module__"):
            if v.__module__ not in unwanted_modules:
                return "Wanted module {} {}".format(v.__module__, v)
        return False

    g = globals().copy()

    def construct_some(cl, classname=""):
        """Construct objects from class `cl`.

        Yields (obj, description) tuples.

        """
        # recursivness
        if getattr(cl, "__name__", None) == "try_to_find_builtins":
            return
        # First yield the class itself
        classname = classname if classname else "{}.{}".format(cl.__module__,
                                                               cl.__name__)
        yield cl, classname

        if cl is print or cl is prnt:  # stop output
            return

        made = False
        for args in constructer_args:
            try:
                obj = cl(*args)
            except Exception:
                continue
            desc = "{}{}".format(classname, args)
            yield obj, desc
            made = True

        if not made:
            # print("Couldn't make a {}".format(classname))
            pass

    def attributes(obj):
        """Produce a sequence of (name, value), the attributes of `obj`."""
        try:
            for n in dir(obj):
                if n in ('__dict__',):
                    continue
                try:
                    if obj.__name__ == "__call__" == n:
                        continue
                except:
                    pass
                try:
                    yield n, getattr(obj, n)
                except Exception:
                    continue
        except Exception:
            pass

    def items(obj):
        """Produce a sequence of (key, value), the items of `obj`."""
        try:
            if isinstance(obj, dict):
                for k in obj.keys():
                    try:
                        yield k, obj[k]
                    except Exception:
                        continue
            elif isinstance(obj, (list, tuple)):
                for k in range(len(obj)):
                    try:
                        yield k, obj[k]
                    except Exception:
                        continue
            elif hasattr(obj, "__iter__"):
                for k in iter(obj):
                    yield "<iter>", k
        except:
            pass

    def attrs_and_items(obj, desc):
        """Produce a sequence of (name, value, desc) for data from `obj`."""
        for n, v in attributes(obj):
            desc2 = "{}.{}".format(desc, n)
            yield n, v, desc2
        for k, v in items(obj):
            desc2 = "{}[{!r}]".format(desc, k)
            yield k, v, desc2
        # examine(j, i, seen, 0)
        for obj2, desc2 in construct_some(obj, desc):
            # desc2 = "{}[{!r}]".format(desc, k)
            yield obj, obj2, desc2

    def examine(obj, desc, seen, depth):
        """Examine the data reachable from `obj`, looking for builtins."""
        if depth >= max_depth:
            return
        if id(obj) in seen:
            return
        if obj is g or obj is examine:  # prevent stack overflow
            return

        seen.add(id(obj))

        # Look at the attributes and items
        for n, v, desc2 in attrs_and_items(obj, desc):
            x = is_builtins(v)
            if x:
                print("Looks like {} might be builtins due to {}".format(desc2,
                                                                         x))
                found[0] += 1
            else:
                examine(v, desc2, seen, depth+1)
    examined = 0
    e = "\r"
    interactive = False
    obj = 1
    print(end="\r")
    msg = colorfy("Trying to find builtins:", color="yellow")
    if obj:
        try:
            for cl in object.__subclasses__():
                seen = set()
                for obj, desc in construct_some(cl):
                    examine(obj, desc, seen, 0)
                examined += len(seen)
                print(msg, "{}/{}".format(found[0], examined), end="\r")
        except Exception:
            pass
    g_ex = 0
    rseen = set()
    for i in range(1):
        for i, j in sorted(g.items()):
            try:
                for obj, desc in construct_some(j, i):
                    examine(obj, desc, rseen, 0)
            except Exception as e:
                print(e)
            print(msg, "{}/{}".format(found[0], examined + len(rseen)),
                  end="\r")
    examined += len(rseen)
    print(msg, "{}/{}".format(found[0], examined), end=" ")
    if found[0]:
        print(found[0])
    doing = False
    return found[0]


def try_to_read_file():
    try:
        open("getme.txt").read()
        return True
    except Exception:
        return False


def try_to_mess_with_str():
    class str(Exception):
        def __init__(self):
            self.s = __builtins__["str"]

        def __eq__(self, *args):
            return True

        def __str__(self):
            return self.s("boo")

        def __repr__(self):
            return self.s("boo")

    #save()
    s = __builtins__["str"]
    __builtins__["str"] = str
    str.__module__ = "builtins"
    suc = False
    try:
        __builtins__[s("__import__")]("hi", "by")
        suc = True
    except Exception as e:
        pass
    str.__module__ = __name__
    return suc


def try_mugging():
    import a_mod
    old_imp = __builtins__["__import__"]
    warnings = type(a_mod)('warnings')

    # Fill it with deception
    warnings.default_action = "ignore"

    # And provide a supporting thug
    def __import__(*args):
        print(args)
        try:
            global sys
            sys = args[1]['sys']
            print("How nice:\n", args[1].keys())
        except Exception as v:
            pass
        return warnings

    # Put the bogus module at the doorstep...
    __builtins__["warnings"] = warnings

    # and have the thug replacing the doorman
    __builtins__["__import__"] = __import__

    # An unsuspecting customer passes by...
    #save()

    # ... and is brutally mugged :)
    try:
        sys.version
        __builtins__["__import__"] = old_imp
        return True
    except:
        __builtins__["__import__"] = old_imp
        return False


def try_to_break_pickling():
    suc = False

    def r(a, b):
        pass

    class A:
        def __reduce__(self):
            try:
                import sys
                suc = True
            except Exception as e:
                suc = False
            return r, (1, 2)

    a = A()
    #save()
    return suc


def try_to_get_open_dill():
    s = [b"\x80\x03cdill.dill\n_import_module\nq\x00X\x04\x00\x00\x00dillq"
         b"\x01X\x00\x00\x00\x00q\x02\x86q\x03Rq\x04.",
         b"\x80\x03cdill.dill\nsys\nq\x00.",
         b"\x80\x03csys\nmodules\nq\x00."]
    for i in s:
        try:
            open = loads(i)
        except ImportError as e:
            pass
        else:
            return True
    return False

func_dict = {"Trying to get round type guard": try_to_get_round_type_guard,
             "Trying to import modules": try_to_import_modules,
             "Trying to find builtins": try_to_find_builtins,
             "Trying to read file": try_to_read_file,
             "Trying to mess with str": try_to_mess_with_str,
             "Trying to do mugging": try_mugging,
             "Trying to break pickling": try_to_break_pickling,
             #"Trying to get open though dill": try_to_get_open_dill
             }

print("Starting tests")

for msg, func in func_dict.items():
    print(colorfy(msg + ": ", color="yellow"), end="")
    #try:
    if func():
        print(colorfy("SUCCEEDED", color="red"))
    else:
        print(colorfy("FAILED", color="green"))
    #except:
    #print(colorfy("FAILED", color="green"))

print("Finished tests")
#print(__builtins__.items())
#print(__builtins__["__import__"])
import a_mod

a_mod.a = 1234567890

#save()
