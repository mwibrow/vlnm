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

def hidden(_):
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

def dataframe(value):
    """Dataframe formatter."""
    if value:
        rows = value.split('\n')
        divs = []
        for i, row in enumerate(rows):
            # columns = re.findall(r'(^\s+|\s*[^\s]+)', row)
            columns = re.findall(r'^\s+|([^\s]+)', row)
            if i == 0:
                for column in columns:
                    div = docutils.nodes.line_block()
                    div.attributes['classes'] += ['dataframe__column']
                    divs.append(div)

            for j, column in enumerate(columns):
                div = docutils.nodes.line_block()
                content = docutils.nodes.inline(column, column)
                div += content
                div.attributes['classes'] += ['dataframe__cell']
                if j == 0:
                    content.attributes['classes'] += ['go']

                else:
                    if i == 0:
                        div.attributes['classes'] += ['dataframe__head']
                        content.attributes['classes'] += ['kn']
                    else:
                        pygments_class = get_pygments_class(column)
                        content.attributes['classes'] += [pygments_class]

                divs[j] += div

        parent = docutils.nodes.line_block()
        parent.attributes['classes'] += ['dataframe highlight']
        parent += divs
        return parent
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
class ConsoleDirective(Directive):
    """Class for processing the :rst:dir:`bibliography` directive.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        'code-only': directives.flag,
        'execute': directives.flag
    }

    def run(self):
        """Run directive"""
        self.arguments = ['python']
        execute = 'code-only' not in self.options

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
                console.append(result)

            if execute:
                stdout, stderr = run_code(interpreter, code_object)
                cast = MAGICS.get(code_magic, MAGICS['console'])
                output = cast(stdout[:-1])
                if output:
                    console.append(output)
                output = MAGICS['console'](stderr[:-1])
                if output:
                    console.append(output)

        parent = docutils.nodes.line_block(classes=['console'])
        for block in console:
            block.attributes['classes'] += ['console-subblock']
            parent += block

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
