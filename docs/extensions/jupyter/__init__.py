"""
Console directive.
"""

import base64
from code import compile_command, InteractiveInterpreter
from contextlib import closing, redirect_stdout, redirect_stderr
import csv
from io import StringIO, BytesIO
import os
import re
import sys
import traceback

from docutils.parsers.rst import directives, Directive
import docutils.nodes
from IPython.core.interactiveshell import InteractiveShell
from pygments import token
from pygments.lexer import RegexLexer
from sphinx.highlighting import lexers
import pandas as pd


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
        header = (
            'import matplotlib\n'
            'matplotlib.use("{}")\n'
            'import matplotlib.pyplot\n'
            '{}\n').format('agg', imports)
        code = '{}\n__figure__ = matplotlib.pyplot.gcf()\n'.format(code)

        env = {}
        exec(header, None, env)  # pylint: disable=exec-used
        _stdout = StringIO()
        _stderr = StringIO()
        with redirect_stdout(_stdout), redirect_stderr(_stderr):
            try:
                exec(code, None, env)  # pylint: disable=exec-used
            except Exception:  # pylint: disable=broad-except
                etype, err, tb = sys.exc_info()
                lineno = traceback.extract_tb(tb)[-1][1]
                line = code.split('\n')[lineno - 1]
                sys.stderr.write('Traceback (most recent call last):\n')
                sys.stderr.write(f'---> {lineno} {line}\n')
                sys.stderr.write(f'{etype.__name__}: {err.args[-1]}')
                # traceback.print_exc(limit=1)

        stdout = _stdout.getvalue()
        stderr = _stderr.getvalue()
        _stdout.close()
        _stderr.close()

        figure = env.get('__figure__')
        image_node = figure_to_node(figure)

        parent = docutils.nodes.line_block(classes=['jupyter'])
        node = docutils.nodes.literal_block(statements, statements, classes=['jupyter-cell'])
        node['language'] = 'python'
        parent += node

        if stdout:
            node = docutils.nodes.literal_block(
                stdout, stdout, classes=['jupyter-output'])
            parent += node

        if stderr:
            node = docutils.nodes.literal_block(
                stderr, stderr, classes=['jupyter-output', 'jupyter-error'])
            node['language'] = 'pytb'
            parent += node

        if image_node:
            parent += image_node

        return [parent]


def figure_to_node(figure):
    """Convert a figure to a docutils image node."""
    if figure and figure.get_axes():
        output = BytesIO()
        figure.savefig(output, format='png', bbox_inches='tight')
        output.seek(0)
        image_data = base64.b64encode(output.getvalue()).decode('ascii')
        output.close()
        image_uri = u'data:image/png;base64,{}'.format(image_data)
        return docutils.nodes.image('', uri=image_uri)
    return None


class IPythonDirective(Directive):
    """Run code in an IPython shell."""
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        shell = InteractiveShell()
        code = u'\n'.join(line for line in self.content)

        with closing(StringIO()) as _stdout, closing(StringIO()) as _stderr:
            with redirect_stdout(_stdout), redirect_stderr(_stderr):
                shell.run_cell(
                    'import matplotlib\n'
                    'matplotlib.use("agg")\n'
                    'import matplotlib.pyplot\n')
                exc_result = shell.run_cell('{}\n'.format(code))

            stdout = _stdout.getvalue()  # pylint: disable=no-member
            # stderr = _stderr.getvalue()  # pylint: disable=no-member

        error = exc_result.error_before_exec or exc_result.error_in_exec
        result = exc_result.result

        parent = docutils.nodes.line_block(classes=['jupyter'])
        input_block = docutils.nodes.line_block(classes=['input'])
        prefix_block = docutils.nodes.line_block(classes=['prefix'])
        prefix_block += docutils.nodes.inline('In:', 'In:')
        input_block += prefix_block
        node = docutils.nodes.literal_block(code, code, classes=['jupyter-cell'])
        node['language'] = 'python'
        input_block += node
        parent += input_block

        output_block = docutils.nodes.line_block(classes=['input'])
        prefix_block = docutils.nodes.line_block(classes=['prefix'])
        prefix_block += docutils.nodes.inline('Out:', 'Out:')
        output_block += prefix_block

        if error:
            # stdout = re.sub(r'\x1b\[\d(?:;\d+)?m', '', stdout)
            stdout = re.sub(
                r'\n.*?(?=Traceback \(most recent call last\))',
                '\n',
                stdout)
            node = docutils.nodes.literal_block(
                stdout, stdout, classes=['jupyter-output'])
            node['language'] = 'ansi-color'
            output_block += node
        else:
            if stdout:
                if isinstance(result, pd.DataFrame):
                    stdout = re.sub(
                        r'Out\[\d+\]:\s*\n{0}$\n'.format(result),
                        '',
                        stdout,
                        flags=re.RegexFlag.DOTALL)
                if stdout:
                    node = docutils.nodes.literal_block(
                        stdout, stdout, classes=['jupyter-output'])
                    parent += node
            if isinstance(result, pd.DataFrame):
                table = typeset_dataframe(result)
                output_block += table
            parent += output_block
        return [parent]


def typeset_dataframe(df):
    """
    Typeset dataframe.
    """
    table = docutils.nodes.table(classes=['dataframe'])
    tgroup = docutils.nodes.tgroup(cols=len(df.columns) + 1)
    table += tgroup

    for _ in range(len(df.columns) + 1):
        colspec = docutils.nodes.colspec(colwidth=1)
        tgroup += colspec

    rows = [make_row([''] + list(df.columns))]

    for row in df.itertuples():
        rows.append(make_row(row))

    thead = docutils.nodes.thead()
    thead.extend(rows[:1])
    tgroup += thead
    tbody = docutils.nodes.tbody()
    tbody.extend(rows[1:])
    tgroup += tbody
    return table


def make_row(row_data):
    """Make a row_node from an iterable of data."""
    row_node = docutils.nodes.row()
    for cell in row_data:
        content = str(cell)
        entry = docutils.nodes.entry()
        entry += docutils.nodes.inline(content, content)
        row_node += entry
    return row_node


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('ipython', IPythonDirective)
    app.add_directive('jupyter', JupyterDirective)
