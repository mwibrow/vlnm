"""
natbib module.

Adapted from https://bitbucket.org/wnielson/sphinx-natbib
"""
import latexcodec

from .cache import CitationCache, BibliographyCache
from .directives import BibliographyDirective
from .nodes import CitationNode, BibliographyNode
from .roles import CitationRole
from .transforms import BibliographyTransform

def init_app(app):
    """
    Initialise the app.
    """
    app.env.bibkeys = CitationCache()
    app.env.bibcache = BibliographyCache()


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
