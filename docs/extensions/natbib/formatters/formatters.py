"""
    Base Formatter class
    ~~~~~~~~~~~~~~~~~~~~
"""

# pylint: disable=no-self-use,unused-argument
import re

import docutils.nodes

from .nodes import (
    boolean, call, emph, field,
    formatted_node, join, optional, sentence, words,
    Node)

def latex_decode(text):
    """
    Decode ascii text latex formant to UTF-8
    """
    return text.encode('ascii').decode('latex')

class Formatter:
    """
    Class for creating citations and bibliographic entries in the APA style.
    """
    def __init__(self):
        self.nodes = []
        self.publications = {}

    @staticmethod
    def sort_keys(keys, bibcache):
        """
        Return a sort key for sorting the bibliography
        """
        if bibcache:
            return keys
        return keys

    def make_entry(self, ref):
        """
        Make a bibliographic entry.
        """
        return ref

    def make_citation(self, bibnode, bibcache, make_refid):
        """
        Create a reference for a citation.
        """

        return bibnode

class Authors(Node):
    """Authors node."""
    def format(self, **kwargs):
        author_list = kwargs.get('entry').persons['author']
        node = formatted_node(
            docutils.nodes.inline,
            '',
            classes=['authors'])
        node += join(sep=', ', last_sep=' and ')[
            [get_author(author) for author in author_list]
        ].format()
        return node

    def __bool__(self):
        return True


class Editors(Node):
    """Edtiors node."""
    def format(self, **kwargs):
        author_list = kwargs.get('entry').persons['editor']
        node = formatted_node(
            docutils.nodes.inline,
            '',
            classes=['editors'])
        node += join(sep=', ', last_sep=' and ')[
            [get_author(author) for author in author_list]
        ].format()
        if len(author_list) > 1:
            node += formatted_node(
                docutils.nodes.inline,
                ' (Eds),')
        else:
            node += formatted_node(
                docutils.nodes.inline,
                ' (Ed),')
        return node

    def __bool__(self):
        return True

def get_author(author):
    """Get an author template."""
    prelast_names = [
        name.render_as('text')
        for name in author.rich_prelast_names]
    last_names = [
        name.render_as('text')
        for name in author.rich_last_names]
    first_names = [
        name.abbreviate().render_as('text')
        for name in author.rich_first_names]
    middle_names = [
        name.abbreviate().render_as('text')
        for name in author.rich_middle_names]
    return join[
        optional[
            boolean[prelast_names],
            words[prelast_names],
            ' '
        ],
        words[last_names],
        ', ',
        words[first_names],
        optional[
            boolean[middle_names],
            ' ',
            words[middle_names]
        ],
    ]

def dashify(string, dash='–'):
    """Replace dashes with unicode dash."""
    try:
        try:
            return re.sub(r'-+', dash, string)
        except TypeError:
            return re.sub(r'-+', dash, string.content)
    except AttributeError:
        return re.sub(r'-+', dash, string.astext())
# pylint: disable=C0103


year = join['(', field['year'], ')']
pages = call[dashify, field['pages']]
title = sentence[field['title']]
journal = emph[field['journal']]
authors = Authors()
editors = Editors()
volume = join[
    field['volume'],
    optional[
        field['number'],
        '(', field['number'], ')'
    ]
]
