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
import sys
import traceback

import docutils.nodes
from docutils.parsers.rst import directives, Directive

from pygments.lexer import RegexLexer
from pygments import token
from sphinx.highlighting import lexers


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
        image_node = None
        if figure and figure.get_axes():
            output = BytesIO()
            figure.savefig(output, format='png', bbox_inches='tight')
            output.seek(0)
            image_data = base64.b64encode(output.getvalue()).decode('ascii')
            image_uri = u'data:image/png;base64,{}'.format(image_data)
            image_node = docutils.nodes.image('', uri=image_uri)

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


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('jupyter', JupyterDirective)
