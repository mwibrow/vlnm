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

@nox.session(python=['3.6'])
def test(session):
    """
    Test
    """
    session.install('-r', 'requirements.txt')
    session.install('-r', 'requirements-dev.txt')
    session.env['PYTHONPATH'] = '.'
    session.run(
        'py.test',
        '--cov=vlnm',
        '--cov-report' 'term-missing')
