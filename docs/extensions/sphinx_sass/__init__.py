"""
    Sphinx Interface
    ~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import codecs
from contextlib import contextmanager
import os
from pathlib import Path
import tempfile
from typing import Tuple, Union

import sass  # pylint: disable=import-self
from sphinx.application import Sphinx

__version__ = '0.0.0'


@contextmanager
def chdir(path: Union[str, Path]):
    """Context manager to temporarily change the working directory."""
    curdir = os.path.abspath(os.curdir)
    try:
        os.chdir(str(path))
        yield
    finally:
        os.chdir(curdir)


def run_sass(app: Sphinx, exception: Exception):  # pylint: disable=unused-argument
    """Run SASS compiler."""
    configs = app.config.sass_configs
    for config in configs:
        compile_sass_config(app, config)


def compile_sass_config(app: Sphinx, config: dict):
    """Compile sass for a particular configuration."""
    build_dir = Path(app.outdir)
    try:
        static_dir = app.config.html_static_path[0]
    except (AttributeError, IndexError):
        static_dir = ''

    entry = Path(config['entry'])
    if not entry.is_absolute():
        entry = Path(app.confdir) / config['entry']
    css_output = build_dir / static_dir / config['output']
    srcmap_output = ''

    compile_options = config.get('compile_options', {})

    source_map = config.get('source_map', '').lower()
    if source_map in ['embed', 'file']:
        compile_options = {key: value for key,
                           value in compile_options.items() if not 'source' in key}
        compile_options['source_map_root'] = 'file://{}'.format(str(entry.parent))
        if source_map == 'file':
            compile_options['source_map_filename'] = '{}{}map'.format(
                css_output.name, os.path.extsep)
        elif source_map == 'embed':
            compile_options['source_map_embed'] = True

    # Sanitize source_map_filename options.
    srcmap_filename = compile_options.get('source_map_filename')
    if srcmap_filename:
        srcmap_output = css_output.parent / srcmap_filename

    # Environment variable overrides.
    if 'SPHINX_SASS_SOURCE_MAPS' in os.environ:
        source_maps = os.environ[
            'SPHINX_SASS_SOURCE_MAPS'].lower() in ['y', 'yes', 'true', '1']
        if source_maps and not srcmap_filename:
            compile_options['source_map_embed'] = True
        else:
            compile_options = {
                key: value for key, value in compile_options.items()
                if not 'source' in key}

    css, srcmap = compile_sass(
        entry,
        compile_options)

    if css:
        if not css_output.parent.exists():
            css_output.parent.mkdir(parents=True)
        with codecs.open(str(css_output), 'w', encoding='utf-8') as file_out:
            file_out.write(css)

    if srcmap and srcmap_output:
        if not srcmap_output.parent.exists():
            srcmap_output.parent.mkdir(parents=True)
        with codecs.open(str(srcmap_output), 'w', encoding='utf-8') as file_out:
            file_out.write(srcmap)


def compile_sass(entry: Union[str, Path], compile_options: dict = None) -> Tuple[str, str]:
    """Compile sass."""

    entry = Path(entry).resolve()  # Just in case we get a pathlib.Path object.
    compile_options = compile_options or {}

    for option in ['filename', 'string', 'filename']:
        compile_options.pop(option, None)

    css, srcmap = '', ''

    with chdir(entry.parent):
        if compile_options.get('source_map_filename'):
            css, srcmap = sass.compile(  # pylint: disable=no-member
                filename=entry.name, **compile_options)
        else:
            css = sass.compile(filename=entry.name, **
                               compile_options)  # pylint: disable=no-member

    return css, srcmap


def init(app: Sphinx):
    """Set up the style sheets."""
    configs = app.config.sass_configs
    for config in configs:
        if config.get('add_css_file', True):
            app.add_css_file(config['output'])


def setup(app: Sphinx):
    """Setup the app."""
    app.add_config_value('sass_configs', [], 'env')
    app.connect('builder-inited', init)
    app.connect('build-finished', run_sass)
