import unittest


class TestCase(unittest.TestCase):
    def assertNotRaises(self):
        class NR:
            def __init__(self, master):
                self.master = master

            def __enter__(self):
                pass

            def __exit__(self, type, value, traceback):
                if type:
                    self.master.fail("It raised a {}({})".format(type, value))
        return NR(self)
