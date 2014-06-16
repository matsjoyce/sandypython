# /bin/python3
import sys
import os
sys.path.append(os.path.abspath('../'))
import unittest
from sandypython import spec
spec.dangerous.remove("f_globals")
spec.dangerous.remove("f_code")
spec.dangerous.remove("tb_frame")
spec.dangerous.remove("tb_next")
spec.dangerous.remove("tb_lineno")
spec.dangerous.remove("co_filename")
spec.dangerous.remove("co_name")

tests = unittest.defaultTestLoader.discover("tests")
runner = unittest.TextTestRunner(verbosity=2, buffer=True).run(tests)
exit(bool(runner.errors or runner.failures))
