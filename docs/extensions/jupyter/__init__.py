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
        options = self.options
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
        node = docutils.nodes.literal_block(code, code, classes=['jupyter-cell'])
        node['language'] = 'python'

        block = jupyter_block(prefix='In: ', children=[node])
        parent += block

        if error:
            stdout = re.sub(
                r'\n.*?(?=Traceback \(most recent call last\))',
                '',
                stdout)
            node = docutils.nodes.literal_block(stdout, stdout, classes=['jupyter-output'])
            node['language'] = 'ansi-color'
            block = jupyter_block(
                prefix='Out: ', prefix_classes=['jupyter-error'], children=[node])
            parent += block
        else:
            nodes, stdout = jupyter_results(result, stdout, **options)
            if stdout:
                node = docutils.nodes.literal_block(
                    stdout, stdout, classes=['jupyter-output'])
                parent += jupyter_block(prefix=' ', children=[node])
            if nodes:
                parent += jupyter_block(prefix='Out:', children=nodes)
        return [parent]


def jupyter_block(prefix=None, prefix_classes=None, children=None):
    prefix_classes = prefix_classes or []
    children = children or []
    block = docutils.nodes.line_block(classes=['jupyter-block'])
    if prefix:
        prefix_block = docutils.nodes.line_block(classes=['jupyter-prefix'] + prefix_classes)
        prefix_block += docutils.nodes.literal(prefix, prefix)
        block += prefix_block
    container = docutils.nodes.line_block(
        classes=(['jupyter-container', 'jupyter-container-prefix']
                 if prefix else ['jupyter-container']))
    for child in children:
        container += child
    block += container
    return block


def jupyter_results(results, stdout, **options):
    """Make jupyter results."""
    stdout = stdout or ''
    if results is not None:
        klass = results.__class__.__name__
        func = f'jupyter_result_{klass.lower()}'
        module = globals()
        if func in module:
            return module[func](results, stdout, **options)
        # Ok try figure.
        try:
            if results.figure:
                return jupyter_result_figure(results.figure, stdout, **options)
        except AttributeError:
            pass
        raise TypeError(f'Unknown jupyter result: {klass}')
    return [], stdout


def jupyter_result_list(results, stdout, **options):
    nodes = []
    for result in results:
        _nodes, stdout = jupyter_results(result, stdout, **options)
        nodes.extend(_nodes)
    return nodes, stdout


def jupyter_result_figure(figure, stdout, **options):
    dpi = options.get('dpi', 150)
    output = BytesIO()
    figure.savefig(output, format='png', bbox_inches='tight', dpi=dpi)
    output.seek(0)
    image_data = base64.b64encode(output.getvalue()).decode('ascii')
    output.close()
    image_uri = u'data:image/png;base64,{}'.format(image_data)
    node = docutils.nodes.image('', uri=image_uri, classes=['jupyter-image'])
    stdout = '\n'.join(stdout.strip().split('\n')[:-1])
    return [node], stdout


def jupyter_result_dataframe(df, stdout, **_options):
    stdout = re.sub(
        r'Out\[\d+\]:\s*\n{0}$\n'.format(df),
        '',
        stdout,
        flags=re.RegexFlag.DOTALL)

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
    return [table], stdout


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
