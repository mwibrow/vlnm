"""
Console directive.
"""

import abc
import base64
from contextlib import closing, contextmanager, redirect_stdout, redirect_stderr
import copy
import csv
from io import StringIO, BytesIO
import os
import pprint
import re
import shutil
import sys
import textwrap
import traceback

from docutils.parsers.rst import directives, Directive
import docutils.nodes
from IPython.core.interactiveshell import InteractiveShell
from pygments import token
from pygments.lexer import RegexLexer
import numpy as np
from sphinx.highlighting import lexers
import pandas as pd
import yaml

import jupyter.html as HTML
from jupyter.shell import get_shell


@contextmanager
def cd(newdir):  # pylint: disable=invalid-name
    """Change working directory."""
    curdir = os.getcwd()
    if newdir != curdir:
        os.chdir(os.path.realpath(os.path.expanduser(newdir)))
    try:
        yield
    finally:
        if newdir != curdir:
            os.chdir(curdir)


class YAMLDirective(Directive):
    """Directive which parses options as YAML"""

    CONFIG = {}

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    def __init__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):

        config, content = self._parse_block_text(block_text)

        super().__init__(
            name, arguments, options, content, lineno, content_offset,
            block_text, state, state_machine)

        if 'configure' in config:
            self.CONFIG.clear()
            self.CONFIG.update(config['configure'])
            del config['configure']
        self.options = self._merge(config, copy.deepcopy(self.CONFIG))

    def _merge(self, source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                self._merge(source[key], node)
            else:
                destination[key] = value
        return destination

    @staticmethod
    def _parse_block_text(block_text):
        lines = block_text.split('\n')[1:]
        config, content = [], []
        target = config
        for line in lines:
            if line.strip() == '':
                target.append(line)
                target = content
            else:
                target.append(line)

        config = textwrap.dedent('\n'.join(config))
        content = textwrap.dedent('\n'.join(content)).split('\n')

        config = yaml.safe_load(config) or {}
        return config, content

    @abc.abstractmethod
    def run(self):
        """Subclasses to override."""


JUPYTER_CONFIG = {}


class JupyterDirective(YAMLDirective):
    """Run code in an IPython shell."""

    CONFIG = JUPYTER_CONFIG

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shell = get_shell()

    def history_node(self, empty=False, classes=None):
        options = self.options
        config = self.state.document.settings.env.config

        history = config.jupyter_history
        if options.get('history') is not None:
            history = history and options.get('history')

        if not history:
            return None

        classes = ['jupyter-history'] + (classes or [])

        if not empty:
            cell_count = self.options.get('cell_count', self.shell.get_cell_count() or 1)
            if cell_count:
                classes.append('jupyter-cell-counts')
                text = f'[{cell_count}]'
        else:
            text = ''

        node = docutils.nodes.line_block(classes=classes)
        node += docutils.nodes.literal(text, text)
        return node

    def normalize_path(self, path):
        path = path or os.getcwd()
        path = path.replace('{root}', os.getcwd())
        path = path.replace('{conf}', self.state.document.settings.env.app.confdir)
        path = path.replace('{tmpdir}', self.shell.tmpdir)
        return path

    def run(self):
        options = self.options
        code = u'\n'.join(line for line in self.content).strip()
        classes = self.options.get('class')
        hide = self.options.get('hide', [])
        run = self.options.get('run', True)

        parent = docutils.nodes.line_block(
            classes=['jupyter'] + ([classes] if classes else []))

        if not run:
            node = docutils.nodes.literal_block(
                code, code,
                classes=['jupyter-terminal' if 'terminal' in options else 'jupyter-cell'])
            node['language'] = 'bash' if 'terminal' in options else 'python'
            block = self.jupyter_block(
                history=self.history_node(empty=True),
                children=[node])
            parent += block
            return [parent]

        if 'reset' in self.options:
            self.shell.reset()

        self.shell.update_user_ns(Sphinx=self.state.document.settings.env.app)

        if 'shell' in options:
            self.shell.run_cell(options['shell'], silent=True)
        if 'before' in options:
            self.shell.run_cell(options['before'], silent=True)

        if 'chdir' in options:
            chdir = self.normalize_path(options['chdir'])
            self.CONFIG.update(path=chdir)
            self.options['path'] = chdir
        path = self.normalize_path(options.get('path'))

        with cd(path):
            exc_result, stdout, _ = self.shell.run_cell(code, silent='silent' in options)

        if 'hidden' in options:
            return []

        if 'code' not in hide:
            node = docutils.nodes.literal_block(code, code, classes=['jupyter-cell'])
            node['language'] = 'python'
            block = self.jupyter_block(
                history=self.history_node(),
                children=[node])
            parent += block

        error = exc_result.error_before_exec or exc_result.error_in_exec
        results = exc_result.result

        if error or stdout or results is not None:
            output = docutils.nodes.line_block(classes=['jupyter-output'])
            if error:
                stdout = re.sub(
                    r'\n.*?(?=Traceback \(most recent call last\))',
                    '',
                    stdout)
                node = docutils.nodes.literal_block(stdout, stdout, classes=['jupyter-stdout'])
                node['language'] = 'ansi-color'
                block = self.jupyter_block(
                    history=self.history_node(classes=['jupyter-error']),
                    children=[node])
                parent += block
            else:
                nodes, stdout = self.jupyter_results(results, stdout, **options)
                if stdout:
                    node = docutils.nodes.literal_block(
                        stdout, stdout, classes=['jupyter-stdout'])
                    node['language'] = self.options.get('highlight-output', 'none')
                    output += self.jupyter_block(
                        history=self.history_node(empty=True), children=[node])
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

        options = self.options.get('dataframe', {})
        index = options.get('index', True)
        formatters = options.get('formatters', {})
        dtypes = options.get('dtypes', {})

        classes = [] if index else ['no-index']
        table = HTML.table(classes=['dataframe'] + classes)

        thead = HTML.thead()
        tbody = None

        row = HTML.tr(classes=['head'])
        if index:
            row += HTML.th(classes=['column-index'])
        for column in df.columns:
            dtype = df[column].dtype.name
            if dtype in HTML.dtypes:
                row += HTML.dtypes[dtype].th(column)
            else:
                row += HTML.th(
                    content=column,
                    classes=['column-{}'.format(column)])
        thead += row

        if not df.empty:
            tbody = HTML.tbody()
            columns = ['index'] + [column for column in df.columns]
            dtypes = [None] + [
                dtypes.get(
                    column,
                    df.iloc[0][column].__class__.__name__) for column in df.columns]
            for i, data in enumerate(df.itertuples()):
                row = HTML.tr(classes=[
                    'row-{}'.format(i + 1),
                    'row-{}'.format('odd' if i % 2 else 'even')
                ])
                for j, zipped in enumerate(zip(data, columns, dtypes)):
                    value, column, dtype = zipped

                    if dtype in HTML.dtypes:
                        row += HTML.dtypes[dtype].td(value, formatters.get(dtype))
                    else:
                        if index or j > 0:
                            classes = ['column-{}'.format(column)]
                            classes.append('column-dtype-{}'.format(dtype))

                            row += HTML.td(content=value, classes=classes)

                tbody += row
        if thead:
            table += thead
        if tbody:
            table += tbody

        raw = table.to_html()
        node = docutils.nodes.raw(raw, raw, format='html')
        return [node], stdout


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


def init_app(app):
    build = app.outdir
    static = app.config.html_static_path

    app.env.gallery = JupyterGallery(build, static[0] if static else '')
    app.add_config_value('jupyter_history', False, 'env')
    app.add_config_value('jupyter_image_format', 'svg', 'env')
    app.add_config_value('jupyter_image_dpi', 96, 'env')
    app.add_config_value('jupyter_cell_counts', False, 'env')


def cleanup(*_args):
    get_shell().cleanup()


def config_app(app, config):
    JUPYTER_CONFIG.update(**config.jupyter_config)
    # Configure SASS
    dirname = os.path.dirname(__file__)
    output = 'jupyter.css'
    config.sass_configs['jupyter'] = dict(
        entry=os.path.join(dirname, 'jupyter.scss'),
        output=output)
    app.add_stylesheet(output)


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.add_config_value('jupyter_config', {}, 'html')
    app.connect('builder-inited', init_app)
    app.connect('build-finished', cleanup)
    app.connect('config-inited', config_app)
    app.add_directive('ipython', JupyterDirective)
    app.add_directive('jupyter', JupyterDirective)
