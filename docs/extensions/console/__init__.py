"""
Console directive.
"""

from code import compile_command, InteractiveInterpreter
from contextlib import redirect_stdout, redirect_stderr
import csv
from io import StringIO
import os
import re

import docutils.nodes
from docutils.parsers.rst import directives, Directive

from pygments.lexer import RegexLexer
from pygments import token
from sphinx.highlighting import lexers

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
class ConsoleDirective(Directive):
    """Class for processing the :rst:dir:`bibliography` directive.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        'code-only': directives.flag,
        'script': directives.flag,
        'execute': directives.flag,
        'lexer': directives.unchanged
    }

    def run(self):
        """Run directive"""
        lexer = self.options.get('lexer') or 'python'
        self.arguments = ['python']

        execute = 'code-only' not in self.options
        env = self.state.document.settings.env



        curdir = os.curdir
        os.chdir(env.relfn2path('')[1])
        local_env = dict(
            __file__=os.path.normpath(env.relfn2path('.')[1]),
            __doc__=None,
            __name__='__console__')
        interpreter = InteractiveInterpreter(locals=local_env)
        if lexer == 'csv':
            content = '\n'.join(self.content)
            console = [csvfile(content)]
        else:
            items = [item for item in self.content]
            console = []
            for line in generate_statements(items, lexer, self.options):
                statement, magic, code_object, code_magic = line

                cast = MAGICS.get(magic, MAGICS['default'])
                result = cast(statement)
                if result:
                    console.append(result)
                if execute and code_magic != 'code':
                    stdout, stderr = run_code(interpreter, code_object)
                    cast = MAGICS.get(code_magic, MAGICS['console'])
                    output = cast(stdout[:-1])
                    if output:
                        console.append(output)
                    output = MAGICS['console'](stderr[:-1])
                    if output:
                        console.append(output)
        os.chdir(curdir)

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

def generate_statements(content, lexer, options):
    """Generator for statements and code_objects.
    """
    if lexer == 'python' and not 'script' in options:
        initial_prefix = '>>> '
        continuation_prefix = '... '
    else:
        initial_prefix = continuation_prefix = ''
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
