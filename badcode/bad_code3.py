def f():
    print(globals().keys())
    print(x)

import a_mod

a_mod.a = 1234567890

save()
