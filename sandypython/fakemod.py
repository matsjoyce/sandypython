class FakeMod:
    def __getattr__(self, name):
        try:
            return self.__dict__["__getattr__"](name)
        except:
            raise AttributeError("Name not in module")


def make_fake_mod(mod_dict):
    mod = FakeMod()

    def getitem(name):
        if name in mod_dict:
            return mod_dict[name]
        else:
            raise AttributeError("Name not in module")
    mod.__getattr__ = getitem
    return mod
