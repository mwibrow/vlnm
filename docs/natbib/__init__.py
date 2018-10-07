"""
natbib module.

Adapted from https://bitbucket.org/wnielson/sphinx-natbib
"""
import codecs
import collections
import os
import re

import docutils.nodes
from docutils import transforms

from docutils.parsers.rst import Directive, directives

import latexcodec

from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import l_, _
from sphinx.roles import XRefRole
from sphinx.errors import SphinxError

from pybtex.database.input import bibtex

from .utils import (KEY, PREV, NEXT, OrderedSet)

from .styles import latex_decode, ApaStyle

from .directives import BibliographyDirective
from .nodes import CitationNode, BibliographyNode
from .roles import CitationRole
from .transforms import BibliographyTransform

def init_app(app):
    """
    Initialise the app.
    """
    app.env.bibkeys = OrderedSet()
    app.env.bibcache = None


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.connect('builder-inited', init_app)
    app.add_role('citep', CitationRole())
    app.add_role('citealp', CitationRole())
    app.add_role('citet', CitationRole())
    app.add_transform(BibliographyTransform)
    app.add_stylesheet('css/style.css')
    app.add_directive('bibliography', BibliographyDirective)
    app.add_node(CitationNode)
    app.add_node(BibliographyNode)
