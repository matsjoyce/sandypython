methods = []
# type stuff
methods += ["mro"]
# string stuff
methods += ["lower", "upper", "islower", "isupper", "isdigit", "isalnum",
            "isalpha", "swapcase", "capitalize", "find", "lstrip", "strip",
            "rstrip", "join", "center", "encode", "decode", "rpartition",
            "rfind", "rjust", "format_map", "translate", "casefold", "rsplit",
            "isprintable", "endswith", "startswith", "isnumeric", "title",
            "ljust", "zfill", "split", "maketrans", "rindex", "replace",
            "isspace", "partition", "istitle", "expandtabs", "splitlines",
            "format", "isidentifier"]
# set stuff
methods += ["union", "difference", "symmetric_difference_update", "add",
            "discard", "isdisjoint", "intersection_update",
            "difference_update", "issubset", "issuperset",
            "symmetric_difference", "intersection"]
# list stuff
methods += ["append", "insert", "sort", "copy", "remove", "pop", "extend",
            "count", "index", "reverse", "clear"]
# int stuff
methods += ["to_bytes", "from_bytes", "bit_length", "numerator", "denominator",
            "isdecimal", "conjugate"]
# float stuff
methods += ["hex", "fromhex", "as_integer_ratio", "imag", "real", "is_integer"]
# dict stuff
methods += ["keys", "values", "items", "update", "get", "popitem",
            "setdefault", "fromkeys"]
# generators
methods += ["send", "throw", "close"]
# splice stuff
methods += ["start", "stop", "step", "indices"]
# property
methods += ["deleter", "getter", "setter", "fdel", "fget", "fset"]
# SyntaxError stuff
methods += ["lineno", "text", "msg", "filename", "print_file_and_line",
            "offset"]
# OSError stuff
methods += ["errno", "strerror", "filename2", "characters_written"]
# BaseException stuff
methods += ["args", "with_traceback"]
# UnicodeErrors stuff
methods += ["reason", "encoding", "end", "object"]
# SystemExit, StopIteration, IOError
methods += ["code", "value", "name", "path"]
# frozen import lib
methods += ["find_module", "find_spec", "get_code", "get_source", "is_package",
            "load_module", "module_repr"]
