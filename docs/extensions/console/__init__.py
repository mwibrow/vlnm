"""
Console directive.
"""

from code import compile_command, InteractiveInterpreter
from contextlib import redirect_stdout
from io import StringIO
import os
import re

import docutils.nodes
from docutils.parsers.rst import directives, Directive
from sphinx.directives import CodeBlock

class ConsoleDirective(CodeBlock):
    """Class for processing the :rst:dir:`bibliography` directive.
    """

    required_arguments = 0

    def run(self):
        """Run directive"""
        env = self.state.document.settings.env

        local_env = dict(
            __file__=os.path.normpath(env.relfn2path('.')[1]),
            __doc__=None,
            __name__='__console__')

        self.arguments = ['python']
        console = []
        code = ''
        code_objects = []
        code_object = None
        initial_prefix = '>>> '
        continuation_prefix = '... '
        magic_prefix = '###'

        statement = initial_prefix
        interpreter = InteractiveInterpreter(locals=local_env)

        hidden = False

        items = [item for item in self.content]
        for item in items:
            if item.startswith(magic_prefix):
                hidden = not hidden
                continue
            line = re.sub(r'^[>.]{3}\s?', '', item)
            code += line
            if code_object:  # from previous iteration.
                if line:
                    statement = initial_prefix + line
            else:
                statement += line
            try:
                code_object = compile_command(code)
                if code_object is None:
                    code += '\n'
                    statement += '\n' + continuation_prefix
                else:
                    code = ''
                    if statement and not hidden:
                        console.append(statement)
                    stdout = StringIO()
                    with redirect_stdout(stdout):
                        interpreter.runcode(code_object)
                    output = stdout.getvalue()
                    stdout.close()
                    if output and not hidden:
                        console.append(output[:-1])
                    statement = ''
                    code_objects.append(code_object)

            except SyntaxError:
                code += r'\n'
                statement += r'\n'
                code_object = None

        self.content = console
        nodes = super(ConsoleDirective, self).run()
        nodes[0].attributes['classes'] = ['console']
        return nodes

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('console', ConsoleDirective)
