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
        code = (
            '\nimport matplotlib\n'
            'matplotlib.use("{}")\n'
            'import matplotlib.pyplot\n'
            '{}\n'
            '{}\n'
            '__figure__ = matplotlib.pyplot.gcf()\n').format('agg', imports, code)
        env = {}
        _stdout = StringIO()
        _stderr = StringIO()
        with redirect_stdout(_stdout), redirect_stderr(_stderr):
            exec(code, env)  # pylint: disable=exec-used
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
        node = docutils.nodes.literal_block(statements, statements)
        node['language'] = 'python'
        parent += node

        if image_node:
            parent += image_node

        return [parent]


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('jupyter', JupyterDirective)
