"""
Console directive.
"""

import base64
from code import compile_command, InteractiveInterpreter
from contextlib import closing, contextmanager, redirect_stdout, redirect_stderr
import csv
from io import StringIO, BytesIO
import os
import pprint
import re
import shutil
import sys
import traceback

from docutils.parsers.rst import directives, Directive
import docutils.nodes
from IPython.core.interactiveshell import InteractiveShell
from pygments import token
from pygments.lexer import RegexLexer
import sass
from sphinx.highlighting import lexers
import pandas as pd


@contextmanager
def cd(newdir):  # pylint: disable=invalid-name
    """Change working directory."""
    curdir = os.getcwd()
    if newdir != curdir:
        os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        if newdir != curdir:
            os.chdir(curdir)


class JupyterDirective(Directive):
    """Run code in an IPython shell."""
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec = {
        'silent': directives.flag,
        'image-dpi': directives.positive_int,
        'image-format': directives.unchanged,
        'image-embed': directives.flag,
        'image-width': directives.unchanged,
        'image-height': directives.unchanged,
        'reset': directives.flag,
        'matplotlib': directives.flag,
        'code-only': directives.flag,
        'path': directives.path
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = get_shell()

    def make_prefix(self, prefix, cell_count):
        options = self.options
        if options.get('history'):
            if options.get('numbers'):
                return f'{prefix}: [{cell_count}]'
            return f'{prefix}:'
        return ''

    def history_node(self, prefix='', empty=False, classes=None):
        options = self.options
        config = self.state.document.settings.env.config

        history = config.jupyter_history
        if options.get('history') is not None:
            history = history and options.get('history')

        if not history:
            return None

        cell_counts = config.jupyter_cell_counts
        if options.get('cell-counts') is not None:
            cell_counts = cell_counts and options.get('cell-counts')

        classes = ['jupyter-history'] + (classes or [])
        if prefix and not empty:
            if history:
                classes.append('jupyter-history')
                text = f'{prefix}:'
            if cell_counts:
                classes.append('jupyter-cell-counts')
                text = f'{prefix}:[{self.shell.get_cell_count()}]'
        else:
            text = ''

        node = docutils.nodes.line_block(classes=classes)
        node += docutils.nodes.literal(text, text)
        return node

    def run(self):
        options = self.options
        code = u'\n'.join(line for line in self.content)

        parent = docutils.nodes.line_block(classes=['jupyter'])

        if 'code-only' in options:
            node = docutils.nodes.literal_block(code, code, classes=['jupyter-cell'])
            node['language'] = 'python'
            block = self.jupyter_block(
                history=self.history_node(empty=True),
                children=[node])
            parent += block
            return [parent]

        if 'reset' in self.options:
            self.shell.reset()

        if 'matplotlib' in self.options:
            self.shell.run_cell(
                'import matplotlib\nmatplotlib.use("agg")\n',
                silent=True)

        path = options.get('path', os.getcwd()) or os.getcwd()
        path = path.replace('{root}', os.getcwd())
        with cd(path):
            exc_result, stdout, _ = self.shell.run_cell(code, silent='silent' in options)

        if 'silent' in options:
            return []

        cell_count = self.shell.get_cell_count()

        node = docutils.nodes.literal_block(code, code, classes=['jupyter-cell'])
        node['language'] = 'python'
        block = self.jupyter_block(
            history=self.history_node('In ', cell_count),
            children=[node])
        parent += block

        error = exc_result.error_before_exec or exc_result.error_in_exec
        results = exc_result.result

        if error or stdout or results:
            output = docutils.nodes.line_block(classes=['jupyter-output'])
            if error:
                stdout = re.sub(
                    r'\n.*?(?=Traceback \(most recent call last\))',
                    '',
                    stdout)
                node = docutils.nodes.literal_block(stdout, stdout, classes=['jupyter-stdout'])
                node['language'] = 'ansi-color'
                block = self.jupyter_block(
                    history=self.history_node('Out', cell_count, classes=['jupyter-error']),
                    children=[node])
                parent += block
            else:
                nodes, stdout = self.jupyter_results(results, stdout, **options)
                if stdout:
                    node = docutils.nodes.literal_block(
                        stdout, stdout, classes=['jupyter-stdout'])
                    node['language'] = 'none'
                    output += self.jupyter_block(
                        history=self.history_node('', empty=True), children=[node])
                if nodes:
                    output += self.jupyter_block(
                        history=self.history_node('Out'),
                        children=nodes)
            parent += output
        return [parent]

    def jupyter_block(self, history=None, children=None):
        """Create a Jupyter cell."""
        children = children or []
        block = docutils.nodes.line_block(classes=['jupyter-block'])
        if history:
            block += history
        container = docutils.nodes.line_block(classes=(['jupyter-container']))
        for child in children:
            container += child
        block += container
        return block

    def jupyter_results(self, results, stdout, **options):
        """Make jupyter results."""
        stdout = stdout or ''
        if results is not None:

            klass = results.__class__.__name__
            func = f'jupyter_result_{klass.lower()}'

            if hasattr(self, func):
                return getattr(self, func)(results, stdout, **options)
            # Ok try figure.
            try:
                if results.figure:
                    return self.jupyter_result_figure(results.figure, stdout, **options)
            except AttributeError:
                pass
            literal = repr(results)
            node = docutils.nodes.literal_block(literal, literal)
            return [node], stdout
        return [], stdout

    def jupyter_result_tuple(self, results, stdout, **options):
        """Create a tuple of results."""
        return self.jupyter_result_list(results, stdout, **options)

    def jupyter_result_list(self, results, stdout, **options):
        """Create a list of results."""
        nodes = []
        if results:
            if len(results) != 1 or 'matplotlib' not in results[0].__class__.__module__:
                stream = StringIO()
                pprint.pprint(results, stream=stream, indent=1, depth=4)
                literal = stream.getvalue()
                stream.close()
                node = docutils.nodes.literal_block(
                    literal, literal)
                nodes.append(node)
            else:
                for result in results:
                    _nodes, stdout = self.jupyter_results(result, stdout, **options)
                    nodes.extend(_nodes)

        return nodes, stdout

    def jupyter_result_type(self, results, stdout, **__):  # pylint: disable=no-self-use
        """Create type."""
        literal = repr(results)
        node = docutils.nodes.literal_block(literal, literal)
        return [node], stdout

    def jupyter_result_figure(self, figure, stdout, **options):
        """Create an image from a matplotlib figure."""
        env = self.state.document.settings.env

        dpi = options.get('image-dpi') or env.config.jupyter_image_dpi
        embed = options.get('embed-image', False)
        fmt = (options.get('image-format') or env.config.jupyter_image_format).lower()

        if embed:
            output = BytesIO()
            figure.savefig(output, format=fmt, bbox_inches='tight', dpi=dpi)
            output.seek(0)
            if fmt == 'svg':
                image_data = '\n'.join(output.getvalue().decode('ascii').split('\n')[4:])
                node = docutils.nodes.raw('', image_data, format='html')
            else:
                data = base64.b64encode(output.getvalue()).decode('ascii')
                uri = u'data:image/{};base64,{}'.format(fmt, data)
                node = docutils.nodes.image('', uri=uri, classes=['jupyter-image'])
            output.close()
        else:
            gallery = env.gallery
            name = f'{gallery.next_image()}.{fmt}'
            path, uri = gallery.image_paths(name)
            figure.savefig(path, format=fmt, bbox_inches='tight', dpi=dpi)
            node = docutils.nodes.raw(
                '', f'<img src="{uri}" class="image jupyter-image" />', format='html')

        stdout = '\n'.join(stdout.strip().split('\n')[:-1])
        return [node], stdout

    def jupyter_result_dataframe(self, df, stdout, **_options):
        """Special typsetting of a dataframe."""
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


def pop_until_match(items, pattern):
    """Pop from list."""
    copy = items[:]
    while copy:
        match = re.match(pattern, copy.pop())
        if match:
            break
    if match:
        return copy
    return items


class JupyterGallery:
    """Helper class for generating names/URIs for linked images."""

    def __init__(self, build, static, images=None):
        images = images or 'jupyter'
        self.path = os.path.join(build, static, images)
        self.uri = os.path.join(static, images)
        if os.path.exists(self.path):
            for path in os.listdir(self.path):
                os.remove(os.path.join(self.path, path))
        else:
            os.makedirs(self.path)

        self.image = 0
        self.images = []

    def next_image(self):
        self.image += 1
        return f'image-{self.image}'

    def image_paths(self, image):
        path = os.path.join(self.path, image)
        uri = os.path.join(self.uri, image)
        self.images.append((image, uri))
        return path, uri


class JupyterShell:
    """Helper class for managing shell interpreters."""

    _instance = None

    def __new__(cls, *__, **___):
        raise RuntimeError(f'Use static get_instance method in instantiate {cls}.')

    def __init__(self):
        self.shell = None
        self.user_ns = {}

    @staticmethod
    def get_instance():
        if JupyterShell._instance is None:
            obj = object.__new__(JupyterShell)
            obj.__init__()
            JupyterShell._instance = obj
        return JupyterShell._instance

    def new(self):
        """Create a new shell."""
        self.shell = InteractiveShell(user_ns=self.user_ns)

    def reset(self):
        """Reset the shell."""
        self.shell.reset()
        self.user_ns = {}
        self.new()

    def get_cell_count(self):
        """Return the last cell number."""
        try:
            return max(self.user_ns.get('Out').keys())
        except (AttributeError, ValueError):
            return None

    def run_cell(self, code, silent=False):
        """Run a cell."""
        if not self.shell:
            self.new()

        with closing(StringIO()) as _stdout, closing(StringIO()) as _stderr:
            with redirect_stdout(_stdout), redirect_stderr(_stderr):
                result = self.shell.run_cell(
                    f'{code}\n',
                    store_history=not silent,
                    silent=silent)

            stdout = _stdout.getvalue()  # pylint: disable=no-member
            stderr = _stdout.getvalue()  # pylint: disable=no-member

        if result:
            pattern = r'^Out\s*\[{}\]'.format(self.get_cell_count())
            stdout = '\n'.join(pop_until_match(stdout.split('\n'), pattern))
        return result, stdout, stderr


def get_shell():
    shell = JupyterShell.get_instance()
    return shell


def init_app(app):
    build = app.outdir
    static = app.config.html_static_path
    setup_sass(os.path.join(build, static[0]))
    app.add_stylesheet('jupyter.css')
    app.env.gallery = JupyterGallery(build, static[0] if static else '')
    app.add_config_value('jupyter_history', False, 'env')
    app.add_config_value('jupyter_image_format', 'svg', 'env')
    app.add_config_value('jupyter_image_dpi', 96, 'env')
    app.add_config_value('jupyter_cell_counts', False, 'env')


def setup_sass(static):
    """Setup sass."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'jupyter.scss'), 'r') as file_in:
        source = file_in.read()
    if source:
        css = sass.compile(string=source)
    else:
        css = ''
    with open(os.path.join(static, 'jupyter.css'), 'w') as file_out:
        file_out.write(css)


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.connect('builder-inited', init_app)
    app.add_directive('ipython', JupyterDirective)
    app.add_directive('jupyter', JupyterDirective)
