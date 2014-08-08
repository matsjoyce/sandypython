import types
import builtins
import sys
import ctypes
from collections import defaultdict
from . import good_special_methods
from . import good_normal_methods

__all__ = ["getsattr", "remove_dangerous_attrs", "replace_dangerous_attrs",
           "stats"]

good_methods = []
good_methods += good_special_methods.methods
good_methods += good_normal_methods.methods

__dict__ = {}

type_list = set()

for mod in (types, builtins):
    for i in dir(mod):
        if isinstance(getattr(mod, i), type):
            type_list.add(getattr(mod, i))

# Thanks to tav.espians.com/a-challenge-to-break-python-security.html
get_dict = ctypes.pythonapi._PyObject_GetDictPtr
get_dict.restype = ctypes.POINTER(ctypes.py_object)
get_dict.argtypes = [ctypes.py_object]


def dictionary_of(ob):
    dptr = get_dict(ob)
    assert dptr and dptr.contents
    return dptr.contents.value

methods = set()
method_origin = {}
for i in type_list:
    methods.update(set(dictionary_of(i)))
    for k in dictionary_of(i):
        if k not in method_origin:
            method_origin[k] = []
        method_origin[k].append(i)

del type_list
dangerous = [i for i in methods if i not in good_methods]

get_mro = dictionary_of(type)["__mro__"].__get__

saved = {}


def getsattr(obj, name, getattr=getattr):
    """
    Mimics the behaviour of the builtin getattr, but works for special methods
    while the sandbox is running.

    Example::

        with utils.ActivateSandbox:
            x = getsattr(object, "__subclasses__")
    """
    if hasattr(obj, name):
        try:
            return getattr(obj, name)
        except:
            pass
    for t in list(get_mro(type(obj))) + [type]:
        if (t, name) in saved:
            return saved[(t, name)].__get__(obj)
    return getattr(obj, name)  # let it make the error message

not_expressed = defaultdict(list)
print = print


def remove_dangerous_attrs():
    """
    Removes all the methods not mentioned in the good_*_methods.py files.
    """
    for i in dangerous:
        for j in method_origin[i]:
            if not hasattr(j, i):
                not_expressed[j].append(i)
            saved[(j, i)] = dictionary_of(j)[i]
            del dictionary_of(j)[i]
            # make sure our modifications is mirrored in the types we modify
            # this is a specialised purpose
            sys._clear_type_cache()
            assert not hasattr(j, i), "{} still has {}".format(j, i)


def replace_dangerous_attrs():
    """
    Replaces all the methods removed by :func:`remove_dangerous_attrs`.
    """
    for i in dangerous:
        for j in method_origin[i]:
            dictionary_of(j)[i] = saved[(j, i)]
            # make sure our modifications is mirrored in the types we modify
            # this is a specialised purpose
            sys._clear_type_cache()
            if i in not_expressed[j]:
                assert i in j.__dict__, "{} still doesn't' have {}" \
                    .format(j, i)
            else:
                assert hasattr(j, i), "{} still doesn't' have {}"\
                    .format(j, i)


def stats():
    """
    Prints some information which may be useful while tweaking the
    good_*_methods.py files
    """
    print("Found", len(methods), "methods")
    print(len(dangerous), "marked for removal")
    print(len(good_methods), "marked as good")
