"""
    Jupyter shell API
    ~~~~~~~~~~~~~~~~~
"""
from contextlib import closing, redirect_stderr, redirect_stdout
from io import StringIO
import re

from IPython import InteractiveShell


def pop_until_match(items, pattern):
    """Pop from list."""
    copy = items[:]
    while copy:
        match = re.match(pattern, copy.pop())
        if match:
            break
    if match:
        return copy
    return items


class JupyterShell:
    """Helper class for managing shell interpreters."""

    _instance = None

    def __new__(cls, *__, **___):
        raise RuntimeError(f'Use static get_instance method in instantiate {cls}.')

    def __init__(self):
        self.shell = None
        self.user_ns = {}

    @staticmethod
    def get_instance():
        if JupyterShell._instance is None:
            obj = object.__new__(JupyterShell)
            obj.__init__()
            JupyterShell._instance = obj
        return JupyterShell._instance

    def new(self):
        """Create a new shell."""
        self.shell = InteractiveShell(user_ns=self.user_ns)

    def reset(self):
        """Reset the shell."""
        self.shell.reset()
        self.user_ns = {}
        self.new()

    def get_cell_count(self):
        """Return the last cell number."""
        try:
            return max(self.user_ns.get('Out').keys())
        except (AttributeError, ValueError):
            return None

    def run_cell(self, code, silent=False):
        """Run a cell."""
        if not self.shell:
            self.new()

        with closing(StringIO()) as _stdout, closing(StringIO()) as _stderr:
            with redirect_stdout(_stdout), redirect_stderr(_stderr):
                result = self.shell.run_cell(
                    f'{code}\n',
                    store_history=not silent,
                    silent=silent)

            stdout = _stdout.getvalue()  # pylint: disable=no-member
            stderr = _stdout.getvalue()  # pylint: disable=no-member

        if result is not None:
            pattern = r'^Out\s*\[{}\]'.format(self.get_cell_count())
            stdout = '\n'.join(pop_until_match(stdout.split('\n'), pattern))
        return result, stdout, stderr


def get_shell():
    """ Return the Jupyter shell."""
    shell = JupyterShell.get_instance()
    return shell
