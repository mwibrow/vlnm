"""
Console directive.
"""

from code import compile_command, InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr
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
        self.arguments = ['python']

        env = self.state.document.settings.env
        local_env = dict(
            __file__=os.path.normpath(env.relfn2path('.')[1]),
            __doc__=None,
            __name__='__console__')
        interpreter = InteractiveInterpreter(locals=local_env)

        items = [item for item in self.content]
        console = []
        for statement, magic, code_object in generate_statements(items):
            if not magic:
                console.append(statement)
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                interpreter.runcode(code_object)
            stdout_output = stdout.getvalue()
            stderr_output = stderr.getvalue()
            stdout.close()
            stderr.close()
            if stdout_output and not magic:
                console.append(stdout_output[:-1])
            if stderr_output:
                console.append(stderr_output[:-1])

        self.content = console
        nodes = super(ConsoleDirective, self).run()
        parent = docutils.nodes.line_block(classes=['console'])
        parent += nodes[0]
        return [parent]

def generate_statements(content):
    """Generator for statements and code_objects.
    """
    hidden = False
    initial_prefix = '>>> '
    continuation_prefix = '... '
    magic_prefix = '###'
    magic = ''
    code_object = None
    code = ''
    statement = initial_prefix
    items = [item for item in content]
    for item in items:
        if item.startswith(magic_prefix):
            hidden = not hidden
            magic = 'hidden' if hidden else ''
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
                if statement:
                    yield (statement, magic, code_object)
                statement = ''
        except SyntaxError:
            code += r'\n'
            statement += r'\n'
            code_object = None

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('console', ConsoleDirective)
