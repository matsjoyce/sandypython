sandypython
===========

Turn your python interpreter into a desert

Warning
=======

This code has not been thoroughly tested yet, so do __not__ use it in anything serious. However, feel free to help test it.

About Sandypython
=================

Sandypython aims to provide a full sandbox that stops the sandboxed code from I/O. It does not aim to stop interpreter crashes.

Features
========

 - Sandboxing
 - Save / load capabillity (though ```sandypython.safe_dill```)

For a more complete reference, see the [docs](https://rawgit.com/matsjoyce/sandypython/master/doc/build/index.html)

For those who want a challenge:
===============================

Place your cracking code in a file with the name bad_code + a number + .py
(```bad_code%d.py```) in the folder badcode, and then call test.py with the number you used.

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
