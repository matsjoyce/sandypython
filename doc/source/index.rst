.. SandyPython documentation master file, created by
   sphinx-quickstart on Sat Jun  7 08:16:22 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SandyPython's documentation!
=======================================

Contents:

.. toctree::
    :maxdepth: 2

    sandypython

To setup a basic sandbox, which does not allow imports::

    from sandypython import *

    core.allow_defaults()
    
    with utils.ActivateSandbox():
        core.exec_str(bad_code)


For those who want a challenge:
===============================

Place your cracking code in a file with the name bad_code + a number + .py
(bad_code%d.py) in the folder badcode, and then call test.py with the number you used.

Targets:
 - Import sys, or any module not in badcode/
 - Read or write a file
 - Turn off the sandbox
 - Retrieve any removed builtin function or type
 - Retrieve __globals__ from a function or any other removed attribute


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Acknowledgements
================

Code stolen from:
 - tav.espians.com/a-challenge-to-break-python-security.html
 - nedbatchelder.com/blog/201302/finding_python_3_builtins.html