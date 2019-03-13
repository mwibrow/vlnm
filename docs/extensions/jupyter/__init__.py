"""
Console directive.
"""

import base64
from code import compile_command, InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr
import csv
from io import StringIO, BytesIO
import os
import re

import docutils.nodes
from docutils.parsers.rst import directives, Directive

from pygments.lexer import RegexLexer
from pygments import token
from sphinx.highlighting import lexers


def hidden(_):  # pylint: disable=useless-return
    """Noop magic."""
    return None


def identity(value):
    """Identity magic."""
    return value


def pycon(value):
    """Console magic."""
    if value:
        node = docutils.nodes.literal_block(value, value)
        node['language'] = 'pycon'
        return node
    return None


def default(value):
    """Default magic."""
    if value:
        node = docutils.nodes.literal_block(value, value)
        node['language'] = 'python'
        return node
    return None


def row_callback(_lexer, match):
    """Process a pandas dataframe row."""
    if match.start() == 0:
        yield match.start(), token.Keyword, match.group(1)
    else:
        line = re.findall(r'(^\s+|\s*[^\s]+|\n)', match.group(1))
        start = match.start()
        for i, item in enumerate(line):
            if i == 0:
                yield start, token.Generic.Output, item
            else:
                try:
                    float(item)
                    yield start, token.Number, item
                except ValueError:
                    if item.strip().lower() in ['na', 'nan']:
                        yield start, token.Generic.Output, item
                    else:
                        yield start, token.String, item
            start += len(item)


class DataFrameLexer(RegexLexer):
    """Crude Pandas datafrane lexer."""
    name = 'pandas'

    tokens = {
        'root': [
            (r'(^.*?\n)', row_callback)
        ]
    }


def csv_row_callback(_lexer, match):
    """Process a pandas dataframe row."""
    row = next(csv.reader(
        [match.group(1)], delimiter=',', quoting=csv.QUOTE_NONE))
    first_row = match.start() == 0
    start = match.start()
    for i, column in enumerate(row):
        if first_row:
            yield start, token.Keyword, column
        else:
            try:
                float(column)
                yield start, token.Number, column
            except ValueError:
                if column.strip().lower() in ['na', 'nan']:
                    yield start, token.Generic.Output, column
                else:
                    yield start, token.String, column
        start += len(column)
        if i < len(row) - 1:
            yield start, token.Generic.Output, ','
            start += 1
    yield start, token.Generic.Output, '\n'
    start += 1


class CsvLexer(RegexLexer):
    """Crude Csv datafrane lexer."""
    name = 'csv'

    tokens = {
        'root': [
            (r'(^.*?\n)', csv_row_callback)
        ]
    }


lexers['pandas'] = DataFrameLexer(startinline=True)
lexers['csv'] = CsvLexer(startinline=True)


def dataframe(value):
    """Dataframe formatter."""
    if value:
        node = docutils.nodes.literal_block(value, value)
        node['language'] = 'pandas'
        return node
    return None


def csvfile(value):
    """csv formatter."""
    if value:
        node = docutils.nodes.literal_block(value, value)
        node['language'] = 'csv'
        return node
    return None


def get_pygments_class(data):
    """Get pygments class."""
    try:
        float(data)
        return 'mi'
    except ValueError:
        pass
    return 's1'


MAGICS = dict(
    default=default,
    hidden=hidden,
    dataframe=dataframe,
    console=pycon
)


class JupyterDirective(Directive):
    """Jupyter style scripting."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        imports = ''
        statements = u'\n'.join(
            line for line in self.content if not line.startswith('###'))
        code = u'\n'.join(
            line[4:] if line.startswith('###') else line for line in self.content)
        code = ('\nimport matplotlib\nmatplotlib.use("{}")\nimport matplotlib.pyplot\n'
                '{}\n{}\n__figure__ = matplotlib.pyplot.gcf()\n').format('agg', imports, code)
        env = {}
        _stdout = StringIO()
        _stderr = StringIO()
        with redirect_stdout(_stdout), redirect_stderr(_stderr):
            exec(code, env)  # pylint: disable=exec-used
        stdout = _stdout.getvalue()
        stderr = _stderr.getvalue()
        _stdout.close()
        _stderr.close()
        if stdout:
            pass
        if stderr:
            pass
        figure = env.get('__figure__')
        if figure and figure.get_axes():
            pass
        parent = docutils.nodes.line_block(classes=['jupyter'])
        code = docutils.nodes.literal_block(statements, statements)
        code['language'] = 'python'
        parent += code

        return [parent]


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('jupyter', JupyterDirective)
