import inspect
from . import core, spec

__all__ = ["DeactivateSandbox", "ActivateSandbox", "check_builtins",
           "type_checker", "type_checker_annotated", "Any", "checked_importer",
           "import_filter_by_name", "import_filter_by_path"]

imported_modules = set()
cols = {i: j for i, j in zip(("black", "red", "green", "yellow", "blue",
                              "magenta", "cyan", "white"), range(30, 38))}


def colorf(*args, color="green"):
    s = " ".join([str(i) for i in args])
    s = "\033[1;%dm%s\033[1;m" % (cols[color], s)
    return s


class DeactivateSandbox:
    """
    Context manager which will call :func:`sandypython.core.end_sandbox`
    if the sandbox was started, then :func:`sandypython.core.start_sandbox`
    if it ended it. It is save to use this without activating the sandbox
    before hand (it will be a no-op).

    Example::

        with utils.DeactivateSandbox:
            open("f.txt")
            import sys

    """
    def __enter__(self):
        self.reinit = core.started
        core.end_sandbox()
        return self

    def __exit__(self, type, value, traceback):
        if self.reinit:
            core.start_sandbox()


class ActivateSandbox:
    """
    Context manager which will call :func:`sandypython.core.start_sandbox`
    if the sandbox has not been started, then
    :func:`sandypython.core.end_sandbox` if it started it. It is save to
    use this with the sandbox already started (it will be a no-op).

    Example::

        with utils.ActivateSandbox:
            core.exec_str(bad_code)

    """
    def __enter__(self):
        self.end = not core.started
        core.start_sandbox()
        return self

    def __exit__(self, type, value, traceback):
        if self.end:
            core.end_sandbox()
