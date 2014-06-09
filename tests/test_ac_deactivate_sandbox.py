import unittest
from sandypython import core, utils


class TestAcDeactivateSandbox(unittest.TestCase):
    def setUp(self):
        core.allow_defaults()

    def test_deactivate(self):
        with utils.DeactivateSandbox():
            self.assertEqual(core.started, False)
        with utils.ActivateSandbox():
            with utils.DeactivateSandbox():
                self.assertEqual(core.started, False)

    def test_activate(self):
        with utils.ActivateSandbox():
            self.assertEqual(core.started, True)
            a = utils.ActivateSandbox()
            a.__enter__()
            self.assertEqual(a.end, False)
            a.__exit__(None, None, None)
            self.assertEqual(core.started, True)

    def tearDown(self):
        core.reset()
