"""
Nox config file.
"""

import nox

@nox.session
def lint(session):
    """
    Lint
    """
    session.install('pylint')
    session.run('pylint', 'vlnm', 'tests')
