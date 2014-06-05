import types
import builtins

__dict__ = {}

type_list = set()

for mod in (types, builtins):
    for i in dir(mod):
        if isinstance(getattr(mod, i), type):
            type_list.add(getattr(mod, i))


def possibly_dangerous(x):
    return any([i in x for i in ("__", "co_", "tb_", "gi_", "im_", "f_")])

good_special_methods = []
# info
good_special_methods += ["doc", "name", "module", "dict", "qualname", "dir"]
# comparison
good_special_methods += ["lt", "le", "eq", "ne", "gt", "ge", "bool"]
# creation and destruction
good_special_methods += ["init", "new", "del"]
# string stuff
good_special_methods += ["str", "repr", "format"]
# container
good_special_methods += ["len", "getitem", "setitem", "delitem", "iter",
                         "reversed", "contains", "hash", "length_hint"]
# arithmetic
good_special_methods += ["add", "sub", "mul", "truediv", "floordiv", "mod",
                         "divmod", "pow", "lshift", "rshift", "and", "or",
                         "xor"]
good_special_methods += ["radd", "rsub", "rmul", "rtruediv", "rfloordiv",
                         "rmod", "rdivmod", "rpow", "rlshift", "rrshift",
                         "rand", "ror", "rxor"]
good_special_methods += ["iadd", "isub", "imul", "itruediv", "ifloordiv",
                         "imod", "idivmod", "ipow", "ilshift", "irshift",
                         "iand", "ior", "ixor"]
good_special_methods += ["neg", "pos", "abs", "invert", "complex", "int",
                         "float", "round", "index", "ceil", "floor", "set",
                         "trunc"]
# context managers
good_special_methods += ["enter", "exit"]
# iterator
good_special_methods += ["next"]
# pickle
good_special_methods += ["reduce", "reduce_ex", "getstate", "setstate",
                         "getnewargs"]
# access
good_special_methods += ["getattr", "setattr", "delattr", "getattribute"]
# size
good_special_methods += ["sizeof"]
# bases
good_special_methods += ["mro", "abstractmethods", "isabstractmethod", "bases"]
# exceptions
good_special_methods += ["cause", "context", "suppress_context"]
# descriptors
good_special_methods += ["get", "set", "delete"]
# functions
good_special_methods += ["call", "annotations", "defaults", "kwdefaults"]
# metaclasses
good_special_methods += ["prepare", "instancecheck", "subclasscheck"]
# possibly dangerous
good_special_methods += ["self", "class", "metaclass", "objclass"]
# super
good_special_methods += ["thisclass"]
# python test stuff
good_special_methods += ["setformat", "getformat"]
# internal python stuff
# good_special_methods += ["dictoffset", "basicsize", "itemsize", "flags"]

good_special_methods = ["__%s__" % i for i in good_special_methods]
good_special_methods += ["co_filename", "co_name", "f_lineno"]
good_special_methods += ["f_back"]  # needed for logging

dangerous_f = lambda x: possibly_dangerous(x) and x not in good_special_methods

methods = set()
method_origin = {}
for i in type_list:
    methods.update(set(i.__dict__))
    for k in i.__dict__:
        if k not in method_origin:
            method_origin[k] = []
        method_origin[k].append(i)

del type_list
dangerous = [i for i in methods if dangerous_f(i)]

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
    print("Found", len(methods), "methods")
    for i in methods:
        if ("_" in i and not dangerous_f(i) and "__" not in i):
            print(i, "is implemented by",
                  ", ".join([str(j)for j in method_origin[i]]))
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
