methods = []
# info
methods += ["doc", "name", "module", "dict", "qualname", "dir"]
# comparison
methods += ["lt", "le", "eq", "ne", "gt", "ge", "bool"]
# creation and destruction
methods += ["init", "new", "del"]
# string stuff
methods += ["str", "repr", "format"]
# container
methods += ["len", "getitem", "setitem", "delitem", "iter", "reversed",
            "contains", "hash", "length_hint"]
# arithmetic
methods += ["add", "sub", "mul", "truediv", "floordiv", "mod", "divmod",
            "pow", "lshift", "rshift", "and", "or", "xor"]
methods += ["radd", "rsub", "rmul", "rtruediv", "rfloordiv", "rmod", "rdivmod",
            "rpow", "rlshift", "rrshift", "rand", "ror", "rxor"]
methods += ["iadd", "isub", "imul", "iand", "ior", "ixor"]
methods += ["neg", "pos", "abs", "invert", "int", "float", "round",
            "index", "ceil", "floor", "set", "trunc"]
# context managers
methods += ["enter", "exit"]
# iterator
methods += ["next"]
# pickle
methods += ["reduce", "reduce_ex", "setstate", "getnewargs"]
# access
methods += ["setattr", "delattr", "getattribute"]
# size
methods += ["sizeof"]
# bases
# methods += ["mro", "abstractmethods", "isabstractmethod", "bases"]
# exceptions
methods += ["cause", "context", "suppress_context"]
# descriptors
methods += ["get", "delete"]
# functions
methods += ["call"]
# methods += ["annotations", "defaults", "kwdefaults"]
# metaclasses
# methods += ["prepare", "instancecheck", "subclasscheck"]
# possibly dangerous
# methods += ["self", "class", "metaclass", "objclass"]
# super
# methods += ["thisclass"]
# python test stuff
# methods += ["setformat", "getformat"]
# internal python stuff
# methods += ["dictoffset", "basicsize", "itemsize", "flags"]

methods = ["__%s__" % i for i in methods]
# methods += ["co_filename", "co_name", "f_lineno"]
# methods += ["f_back"]  # needed for logging
