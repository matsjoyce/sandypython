import unittest
from sandypython import core, utils


class TestAcDeactivateSandbox(unittest.TestCase):
    def setUp(self):
        core.add_default_builtins()

    def test_deactivate(self):
        with utils.DeactivateSandbox():
            self.assertEqual(core.started, False)
        with utils.ActivateSandbox():
            with utils.DeactivateSandbox():
                self.assertEqual(core.started, False)

    def test_activate(self):
        with utils.ActivateSandbox():
            self.assertEqual(core.started, True)
            with utils.ActivateSandbox() as a:
                self.assertEqual(a.end, False)
            self.assertEqual(core.started, True)

    def tearDown(self):
        core.reset()
