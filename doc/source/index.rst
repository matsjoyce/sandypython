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



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

