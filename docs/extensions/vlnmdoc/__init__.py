"""
Some VLNM-specific stuff.
"""
from distutils.dir_util import copy_tree
import importlib
import os
import re

import docutils.nodes
import docutils.utils
import docutils.statemachine
from sphinx.util.docutils import SphinxDirective


import vlnm
from vlnm import get_normalizer, list_normalizers

from .fonts import setup_fonts
from .normalizers import (
    NormalizersListDirective,
    NormalizerSummariesDirective,
    NormalizersTableDirective)


def make_inline(tag, cls=None):
    """Create a simple inline role."""
    cls = cls or tag

    def _inline(
            typ, rawtext, text, lineno, inliner,  # pylint: disable=unused-argument
            options=None, content=None):  # pylint: disable=unused-argument
        return [docutils.nodes.inline(text, text, classes=[f'vlnm-{cls}'])], []
    return _inline


WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))


def init_app(app):

    build_dir = app.outdir
    try:
        static_dir = app.config.html_static_path[0]
    except (AttributeError, IndexError):
        static_dir = ''

    vlnm_dir = 'vlnm'
    font_dir = os.path.join(vlnm_dir, 'fonts')
    font_path = os.path.join(build_dir, static_dir, font_dir)
    setup_fonts(font_path)


def config_app(app, config):

    static_dir = app.config.html_static_path[0]
    vlnm_dir = 'vlnm'
    font_dir = os.path.join(static_dir, vlnm_dir, 'fonts')

    dirname = os.path.dirname(__file__)
    output = 'vlnm/css/vlnm.css'
    config.sass_configs['vlnm'] = dict(
        entry=os.path.join(dirname, 'styles', 'main.scss'),
        output=output,
        variables={'font-dir': font_dir})
    app.add_stylesheet(output)


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.setup_extension('sass_compile')

    # setup_highlighter(app)
    app.config.pygments_style = 'material'
    app.connect('builder-inited', init_app)
    app.connect('config-inited', config_app)
    for role in ['col', 'arg', 'tt', 'csv']:
        app.add_role(role, make_inline(role))

    app.add_directive('normalizers-list', NormalizersListDirective)
    app.add_directive('normalizers-table', NormalizersTableDirective)
    app.add_directive('normalizers-summaries', NormalizerSummariesDirective)
