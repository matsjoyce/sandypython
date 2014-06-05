import types
import builtins
import sys
import ctypes
from collections import defaultdict
try:
    from . import good_special_methods
    from . import good_normal_methods
except:
    import good_special_methods
    import good_normal_methods

good_methods = []
good_methods += good_special_methods.methods
good_methods += good_normal_methods.methods

__dict__ = {}

type_list = set()

for mod in (types, builtins):
    for i in dir(mod):
        if isinstance(getattr(mod, i), type):
            type_list.add(getattr(mod, i))

get_dict = ctypes.pythonapi._PyObject_GetDictPtr
get_dict.restype = ctypes.POINTER(ctypes.py_object)
get_dict.argtypes = [ctypes.py_object]


def dictionary_of(ob):
    dptr = get_dict(ob)
    if dptr and dptr.contents:
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

get_mro = dictionary_of(type)['__mro__'].__get__

saved = {}


def getsattr(obj, name, type_=None):
    if type_ is None:
        type_ = type(obj)
    for t in list(get_mro(type_)) + [type]:
        if (t, name) in saved:
            return saved[(t, name)].__get__(obj)
        if hasattr(obj, name):
            return getattr(obj, name)

not_expressed = defaultdict(list)


def remove_dangerous_attrs():
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
    for i in dangerous:
        for j in method_origin[i]:
            dictionary_of(j)[i] = saved[(j, i)]
            # make sure our modifications is mirrored in the types we modify
            # this is a specialised purpose
            sys._clear_type_cache()
            if i in not_expressed[j]:
                assert i in j.__dict__, "{} still doesn't' have {}".format(j, i)
            else:
                assert hasattr(j, i), "{} still doesn't' have {}".format(j, i)

if __name__ == "__main__":
    import _frozen_importlib
    print("Found", len(methods), "methods")
    print(len(dangerous), "marked for removal")
    print(len(good_methods), "marked as good")

    print()
    for i in sorted(dangerous):
        print(i, "is implemented by",
              ", ".join([str(j) for j in method_origin[i]]))

    remove_dangerous_attrs()

    try:
        types.FunctionType.__code__
    except Exception as e:
        print(e)

    try:
        TypeError().tb_frame
    except Exception as e:
        print(e)

    replace_dangerous_attrs()
