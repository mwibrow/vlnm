"""
    New Formatters
    ~~~~~~~~~~~~~~
"""
# pylint: disable=W0621

import docutils.nodes
from docutils.nodes import inline, reference

from .nodes import (
    join, emph, sentence
)

from .formatters import (
    Formatter,
    latex_decode,
    authors, editors, field, journal, pages, title, volume, year)

class AuthorYearFormatter(Formatter):
    """
    Class for creating citations and bibliographic entries in the APA style.
    """

    @staticmethod
    def article_template():
        """Template for an article."""
        return join(sep=' ')[
            sentence[join[authors, ', ', year]],
            title,
            join[journal, ', ', volume, ' ', pages, '.']
        ]

    @staticmethod
    def phdthesis_template():
        """Template for a PhD thesis."""
        return join(sep=' ')[
            sentence[join[authors, ', ', year]],
            emph[title],
            sentence[field['school']]
        ]

    @staticmethod
    def inproceedings_template():
        """Template for inproceedings entry."""
        return join(sep=' ')[
            sentence[join[authors, ', ', year]],
            emph[title],
            sentence[field['booktitle']]
        ]

    @staticmethod
    def incollection_template():
        """Template for incollection entry."""
        return join(sep=' ')[
            sentence[join[authors, ', ', year]],
            emph[title],
            sentence[
                'In',
                editors,
                join[
                    field['booktitle'],
                    ','
                ],
                volume,
                pages
            ]
        ]

    @staticmethod
    def sort_keys(keys, bibcache):
        """
        Return a sort key for sorting the bibliography
        """
        def _sort_key(key):
            return bibcache[key].persons.get('author')[0].last()[0]
        return sorted(keys, key=_sort_key)

    def make_entry(self, ref):
        """
        Make a bibliographic entry.
        """
        ref_node = docutils.nodes.paragraph(
            '', '', classes=[ref.type, 'reference'])

        method = '{}_template'.format(ref.type)
        if hasattr(self, method):
            template = getattr(self, method)
            nodes = template().format(entry=ref)
            ref_node += nodes
        else:
            print(method)
        return ref_node

    def make_citation(self, bibnode, bibcache, make_refid):  # pylint: disable=R0201
        """
        Create a reference for a citation.
        """
        typ = bibnode.data['typ']
        if typ in ['citep', 'citealp']:
            return make_citep(bibnode, bibcache, make_refid)
        if typ in ['citet']:
            return make_citet(bibnode, bibcache, make_refid)

        return bibnode


def make_citep(bibnode, bibcache, make_refid):
    """
    Make the citation text for :rst:role:citep: and :rst:role:citealp: roles.
    """
    node = inline('', '')
    classes = ['xref', 'cite']
    typ = bibnode.data['typ']
    keys = bibnode.data['keys']
    pre_text = bibnode.data.get('pre_text')
    post_text = bibnode.data.get('post_text')
    if typ != 'citealp':
        node += inline('(', '(')
    if pre_text:
        text = '{} '.format(pre_text)
        node += inline(text, text)
    for i, key in enumerate(keys):
        entry = bibcache[key]
        refid = make_refid(entry, bibnode.data['docname'])

        authors = entry.persons.get('author')
        text = get_citation_author_text(authors)

        refnode = reference(
            text, text, internal=True, refuri='#{}'.format(refid),
            classes=classes)
        node += refnode

        year = entry.fields.get('year')
        if year:
            node += inline(', ', ', ')
            refnode = reference(
                year, year, internal=True, refuri='#{}'.format(refid),
                classes=classes)
            node += refnode

        if len(keys) > 1:
            if i < len(keys) - 1:
                node += inline('; ', '; ')
    if post_text:
        if post_text.startswith(','):
            text = post_text
        else:
            text = ' {}'.format(post_text)
        node += inline(text, text)
    if typ != 'citealp':
        node += inline(')', ')')

    return node

def get_citation_author_text(authors):
    """
    Get the citation text for an author.
    """
    text = ''
    if len(authors) == 1:
        text = latex_decode(authors[0].last()[0])
    elif len(authors) == 2:
        names = [latex_decode(name.last()[0]) for name in authors]
        text += ' & '.join(names)
    else:
        name = latex_decode(authors[0].last()[0])
        text = '{} et al.'.format(name)
    return text

def make_citet(bibnode, bibcache, make_refid):
    """
    Make the citation text for a :rst:role:citet: role.
    """
    node = inline('', '')
    classes = ['xref', 'cite']
    typ = bibnode.data['typ']
    keys = bibnode.data['keys']
    pre_text = bibnode.data.get('pre_text')
    post_text = bibnode.data.get('post_text')
    if typ in ['citet']:
        for key in keys:
            entry = bibcache[key]
            refid = make_refid(entry, bibnode.data['docname'])

            authors = entry.persons.get('author')
            text = get_citation_author_text(authors)

            refnode = docutils.nodes.reference(
                text, text, internal=True, refuri='#{}'.format(refid),
                classes=classes)
            node += refnode

            year = entry.fields.get('year')
            if year:
                node += inline(' (', ' (')
                if pre_text:
                    text = '{} '.format(pre_text)
                    node += inline(text, text)

                refnode = docutils.nodes.reference(
                    year, year, internal=True, refuri='#{}'.format(refid),
                    classes=classes)
                node += refnode
                if post_text:
                    if post_text.startswith(','):
                        text = post_text
                    else:
                        text = ' {}'.format(post_text)
                    node += inline(text, text)
                node += inline(')', ')')

    return node
