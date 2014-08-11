sandypython
===========

Turn your python interpreter into a desert

Warning
=======

This code has not been thoroughly tested yet, so do __not__ use it in anything serious. However, feel free to help test it.

About SandyPython
=================

SandyPython aims to provide a full sandbox that stops the sandboxed code from I/O. It does not aim to stop interpreter crashes.

[![Build Status](https://travis-ci.org/matsjoyce/sandypython.svg?branch=master)](https://travis-ci.org/matsjoyce/sandypython)

Features
========

 - Sandboxing
 - Save / load capabillity (though ```sandypython.safe_dill```)
 - Module whitelist
 - Method whitelist for all builtin types
 - Object modification checking
 - Full sphinx [documentation](https://rawgit.com/matsjoyce/sandypython/master/doc/build/index.html)

Quick start:
```py3
from sandypython import *

core.add_default_builtins()

with utils.ActivateSandbox():
    core.exec_str(bad_code)
```

For a more complete reference, see the [docs](https://rawgit.com/matsjoyce/sandypython/master/doc/build/index.html)

For those who want a challenge:
===============================

Place your cracking code in a file with the name bad_code + a number + .py
(```bad_code%d.py```) in the folder badcode, and then call test.py with the number you used.
I.E. If you have called your program ```bad_code5.py```, execute ```python test.py 5```

Targets:
 - Import ```sys```, or any module not in badcode/
 - Read or write a file
 - Turn off the sandbox
 - Retrieve any removed builtin function or type
 - Retrieve ```__globals__``` from a function or any other removed attribute

Please report all breakthroughs as an issue.

Licence
=======

All code GPLv3 except where code is from a external source (shown in code), where the licence is that of the external source
