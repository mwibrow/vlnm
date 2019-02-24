"""
Extension providing custom lexers.
"""
import setuptools

from pygments.lexers.python import Python3Lexer
from sphinx.highlighting import lexers

class Python3LexerExtended(Python3Lexer):
    aliases = ['py3ext']
    name = 'py3ext'


ENTRY_POINTS = """
[pygments.lexers]
py3ext=extensions.lexers:Python3LexerExtended
"""

def setup(_app):
    setuptools.setup(
        script_name='setup.py',
        script_args=['install'],
        name='lexers',
        version='0.1',
        description=__doc__,
        author='Mark Wibrow',
        packages=['extensions.lexers'],
        entry_points=ENTRY_POINTS)
