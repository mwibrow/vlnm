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

def noop(_):
    """Noop magic."""
    return None

def identity(value):
    """Identity magic."""
    return value

def csv(value):
    """CSV magic."""
    return value

MAGICS = dict(
    default=identity,
    hidden=noop,
    csv=identity
)
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
        for line in generate_statements(items):
            statement, magic, code_object, code_magic = line
            cast = MAGICS.get(magic, MAGICS['default'])
            result = cast(statement)
            if result:
                console.append(statement)

            stdout, stderr = run_code(interpreter, code_object)
            cast = MAGICS.get(code_magic, MAGICS['default'])
            stdout_output = cast(stdout)
            stderr_output = cast(stderr)

            if stdout_output:
                console.append(stdout_output[:-1])
            if stderr_output:
                console.append(stderr_output[:-1])

        self.content = console
        nodes = super(ConsoleDirective, self).run()
        parent = docutils.nodes.line_block(classes=['console'])
        parent += nodes[0]
        return [parent]

def run_code(interpreter, code_object):
    """Run a code_object and return output."""
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        interpreter.runcode(code_object)
    stdout_output = stdout.getvalue()
    stderr_output = stderr.getvalue()
    stdout.close()
    stderr.close()
    return stdout_output, stderr_output

def generate_statements(content):
    """Generator for statements and code_objects.
    """
    initial_prefix = '>>> '
    continuation_prefix = '... '
    magic_prefix = '### '
    magic = ''
    code_magic = ''
    code_object = None
    code = ''
    statement = initial_prefix
    items = [item for item in content]
    for item in items:
        if item.startswith(magic_prefix):
            magic = 'hidden'
            item = item[len(magic_prefix):]
        else:
            match = re.match(r'^(.*)\s+{}(.*)\s*?$'.format(magic_prefix), item)
            if match:
                item, code_magic = match.groups()

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
                if statement:
                    yield (statement, magic, code_object, code_magic)
                code = code_magic = magic = statement = ''
        except SyntaxError:
            code += r'\n'
            statement += r'\n'
            code_object = None

def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_directive('console', ConsoleDirective)
