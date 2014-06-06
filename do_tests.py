#/bin/python3
import sys
import unittest
from sandbox import spec
spec.dangerous.remove("f_globals")

tests = unittest.defaultTestLoader.discover("tests")
unittest.TextTestRunner(verbosity=2, buffer=True).run(tests)
