"""
natbib module.

Adapted from https://bitbucket.org/wnielson/sphinx-natbib
"""

import docutils.nodes

import latexcodec

from .formatters.authoryear import AuthorYearFormatter
from .cache import CitationCache, BibliographyCache
from .directives import BibliographyDirective
from .nodes import CitationNode, BibliographyNode
from .roles import CitationRole, small_caps_role
# from .transforms import BibliographyTransform

def init_app(app):
    """
    Initialise the app.
    """
    app.env.bibkeys = CitationCache()
    app.env.bibcache = BibliographyCache()


def process_bibliographies(app, doctree, docname):
    """
    Process bibliography nodes.
    """

    env = app.env
    bibcache = env.bibcache
    bibkeys = env.bibkeys

    for bibnode in doctree.traverse(BibliographyNode):
        cite_all = bibnode.data['all']
        docname = bibnode.data['docname']
        keys = bibkeys.get_keys(None if cite_all else docname)
        formatter = AuthorYearFormatter(env)

        node = docutils.nodes.paragraph()
        keys = formatter.sort_keys(keys, bibcache)

        year_suffixes = formatter.resolve_ties(keys, bibcache)
        for key in year_suffixes:
            bibcache[key].fields['year_suffix'] = year_suffixes[key]

        for key in keys:
            refid = '{}'.format(key)
            entry = formatter.make_entry(bibcache[key])
            entry['ids'] = entry['names'] = [refid]
            node += entry
        bibnode.replace_self(node)

        for key in year_suffixes:
            bibcache[key].fields['year_suffix'] = ''

def process_citations(app, doctree, docname):
    """
    Process citations:
    """

    formatter = AuthorYearFormatter(app.env)
    bibcache = app.env.bibcache
    bibkeys = app.env.bibkeys

    bibdocs = list(bibcache.cache.keys())
    if len(bibdocs) == 1:
        docname = '{}.html'.format(bibdocs[0])

    keys = bibkeys.get_keys()
    year_suffixes = formatter.resolve_ties(keys, bibcache)
    for key in year_suffixes:
        bibcache[key].fields['year_suffix'] = year_suffixes[key]

    for citenode in doctree.traverse(CitationNode):
        node = formatter.make_citation(
            citenode, bibcache, docname)
        citenode.replace_self(node)

    for key in year_suffixes:
        bibcache[key].fields['year_suffix'] = ''


def setup(app):
    """
    Set up the sphinx extension.
    """
    app.connect('builder-inited', init_app)
    app.connect('doctree-resolved', process_bibliographies)
    app.connect('doctree-resolved', process_citations)
    app.add_role('citep', CitationRole())
    app.add_role('citeps', CitationRole())
    app.add_role('citealp', CitationRole())
    app.add_role('citet', CitationRole())
    app.add_role('citets', CitationRole())
    app.add_role('citealt', CitationRole())
    app.add_role('cite', CitationRole())
    app.add_role('smallcaps', small_caps_role)
    app.add_stylesheet('css/style.css')
    app.add_directive('bibliography', BibliographyDirective)
    # app.add_transform(BibliographyTransform)
    app.add_node(CitationNode)
    app.add_node(BibliographyNode)
