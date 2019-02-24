"""
Extension providing custom lexers.
"""
import setuptools

from pygments.lexer import combined, include, bygroups, using, default, words
from pygments.lexers.python import Python3Lexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.token import Comment, Keyword, Name, Operator, Punctuation, String, Text
from sphinx.highlighting import lexers


class Python3LexerExtended(Python3Lexer):
    """Extended python 3 lexer."""

    aliases = ['py3ext']
    name = 'py3ext'

    tokens = Python3Lexer.tokens.copy()

    tokens['root'] = [
        (r'\n', Text),
        (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")', bygroups(Text, String.Affix, String.Doc)),
        (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')", bygroups(Text, String.Affix, String.Doc)),
        (r'[^\S\n]+', Text),
        (r'\A#!.+$', Comment.Hashbang),
        (r'#.*$', Comment.Single),
        (r'[]{}:(),;[]', Punctuation),
        (r'\\\n', Text),
        (r'\\', Text),
        (r'(in|is|and|or|not)\b', Operator.Word),
        (r'!=|==|<<|>>|[-~+/*%=<>&^|.]', Operator),
        include('keywords'),
        (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
        (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
        (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text), 'fromimport'),
        (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text), 'import'),
        include('builtins'),
        include('magicfuncs'),
        include('magicvars'),
        include('backtick'),
        include('strings'),
        include('name'),
        include('numbers'),
    ]

    tokens['strings'] = [
        ('(?i)(r[fub]?|[fub]r)(""")',
         bygroups(String.Affix, String.Double), 'tdqs'),
        ("(?i)(r[fub]?|[fub]r)(''')",
         bygroups(String.Affix, String.Single), 'tsqs'),
        ('(?i)(r[fub]?|[fub]r)(")',
         bygroups(String.Affix, String.Double), 'dqs'),
        ("(?i)(r[fub]?|[fub]r)(')",
         bygroups(String.Affix, String.Single), 'sqs'),
        ('(?i)([ubf]?)(""")', bygroups(String.Affix, String.Double),
         combined('stringescape', 'tdqs')),
        ("(?i)([ubf]?)(''')", bygroups(String.Affix, String.Single),
         combined('stringescape', 'tsqs')),
        ('(?i)([ubf]?)(")', bygroups(String.Affix, String.Double),
         combined('stringescape', 'dqs')),
        ("(?i)([ubf]?)(')", bygroups(String.Affix, String.Single),
         combined('stringescape', 'sqs')),
    ]

ENTRY_POINTS = """
[pygments.lexers]
py3ext = extensions.lexers:Python3LexerExtended
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
