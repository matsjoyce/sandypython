import unittest
from sandypython import core, utils


class TestAcDeactivateSandbox(unittest.TestCase):
    def setUp(self):
        core.add_default_builtins()
        with self.assertRaises(RuntimeError):
            core.add_to_exec_globals("a", lambda x: x)
        with self.assertRaises(RuntimeError):
            core.add_builtin("a", lambda x: x)
        self.started = False
        core.on_start(self.on_start)
        core.on_end(self.on_end)

    def on_start(self):
        self.started = True

    def on_end(self):
        self.started = False

    def test_deactivate(self):
        with utils.DeactivateSandbox():
            self.assertEqual(core.started, False)
            self.assertEqual(self.started, False)
        with utils.ActivateSandbox():
            with utils.DeactivateSandbox():
                self.assertEqual(core.started, False)
                self.assertEqual(self.started, False)

    def test_activate(self):
        self.assertEqual(self.started, False)
        with utils.ActivateSandbox():
            self.assertEqual(self.started, True)
            self.assertEqual(core.started, True)
            with utils.ActivateSandbox() as a:
                self.assertEqual(a.end, False)
            self.assertEqual(core.started, True)
        self.assertEqual(self.started, False)

    def tearDown(self):
        core.reset()
