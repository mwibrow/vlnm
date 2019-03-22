"""
    New Formatters
    ~~~~~~~~~~~~~~
"""
# pylint: disable=W0621
from collections import OrderedDict

import docutils.nodes

from .nodes import (
    boolean, ifelse, idem, join, emph, optional, ref, sentence, text, url
)

from .formatters import (
    Formatter,
    authors, doi, editors, field, journal, pages, title, volume, year)


class AuthorYearFormatter(Formatter):
    """
    Class for creating citations and bibliographic entries in the APA style.
    """

    @staticmethod
    def article_template():
        """Template for an article."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            title,
            join[journal, ', ', volume, ' ', pages, '.'],
            optional[field['doi'], doi]
        ]

    @staticmethod
    def online_template():
        """Tempalte for an online reference."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            title,
            'Online resource:',
            url[join[field['url']]],
            join['(accessed ', field['accessed'], ')']
        ]

    @staticmethod
    def phdthesis_template():
        """Template for a PhD thesis."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            emph[title],
            text['PhD Dissertation, '],
            sentence[field['school']]
        ]

    @staticmethod
    def inproceedings_template():
        """Template for inproceedings entry."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            emph[title],
            sentence[field['booktitle']],
            optional[pages, sentence[pages]]
        ]

    @staticmethod
    def incollection_template():
        """Template for incollection entry."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            emph[title],
            sentence[
                'In',
                editors,
                join[
                    field['booktitle'],
                    ','
                ],
                optional[volume],
                optional[field['publisher']],
                pages
            ]
        ]

    @staticmethod
    def book_template():
        """Template for book entry."""
        return join(sep=' ')[
            sentence[join[authors, ', ', join['(', year, ')']]],
            join(sep='')[
                emph[field['title']],
                optional[field['volume'], ', volume ', volume],
                '.'
            ],
            sentence[field['publisher']]
        ]

    @staticmethod
    def sort_key():
        """Template for the key used to sort bibliography entries."""
        return join[authors, year, title]

    @staticmethod
    def sort_keys(keys, bibcache):
        """
        Return a sort key for sorting the bibliography
        """
        def _sort_key(key):
            entry = bibcache[key]
            return AuthorYearFormatter.sort_key().format(entry=entry).astext()
        return sorted(keys, key=_sort_key)

    @staticmethod
    def resolve_ties(keys, bibcache):
        """Creat year suffixes from a sorted list of keys."""

        if len(keys) < 2:
            return {}

        def sort_key(k):
            return join[authors, year].format(
                entry=bibcache[keys[k]]).astext()

        sort_key_j = sort_key(0)
        suffixes = {}
        for i in range(0, len(keys) - 1):
            j = i + 1
            sort_key_i = sort_key_j
            sort_key_j = sort_key(j)
            if sort_key_i == sort_key_j:
                if keys[i] not in suffixes:
                    suffixes[keys[i]] = 'a'
                suffixes[keys[j]] = chr(ord(suffixes[keys[i]]) + 1)

        return suffixes

    @staticmethod
    def make_refid(entry, docname):
        """Make a reference id."""
        if docname == AuthorYearFormatter.env.config.master_doc:
            docname = ''
        return '{}#{}'.format(docname, entry.key)

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

    def make_citation(self, citenode, bibcache, docname):
        """
        Create a reference for a citation.
        """
        typ = citenode.data['typ']

        if typ in ['citep', 'citeps', 'citealp']:
            return self.citep(citenode, docname, bibcache)
        if typ in ['citet', 'citets', 'citealt']:
            return self.citet(citenode, docname, bibcache)
        if typ in ['cite']:
            return self.cite(citenode, docname, bibcache)
        return citenode

    @staticmethod
    def citet(citenode, docname, bibcache):
        """Textual citation."""
        typ = citenode.data['typ']
        starred = typ.endswith('s')
        parenthesis = typ != 'citealt'
        tokens = citenode.data['tokens']
        pre_text, keys, post_text = tokens[:3]
        if len(keys) > 1 or starred:
            pre_text = post_text = ''
        groups = get_key_groups(keys, bibcache)
        return join(sep='; ')[[
            join[
                ifelse[
                    boolean[True],  # Why
                    ref(classes=['natbib'])[
                        authors(
                            last_names_only=True,
                            last_sep=' and ' if starred else ' & ',
                            et_al=not starred)
                    ].format(entry=bibcache[group[0]], docname=docname),
                ],
                ' ',
                optional[boolean[parenthesis], '('],
                optional[pre_text],
                join(sep=', ')[[
                    ifelse[
                        boolean[i > 0],
                        ref(classes=['natbib'])[field['year_suffix']].format(
                            entry=bibcache[key], docname=docname),
                        ref(classes=['natbib'])[year].format(
                            entry=bibcache[key], docname=docname)
                    ]
                    for i, key in enumerate(group)
                ]],
                optional[post_text],
                optional[boolean[parenthesis], ')']
            ] for group in groups
        ]].format()

    @staticmethod
    def citep(citenode, docname, bibcache):
        """Parenthetical citation."""
        typ = citenode.data['typ']
        starred = typ.endswith('s')
        parenthesis = not typ.endswith('alp')
        tokens = citenode.data['tokens']
        pre_text, keys, post_text = tokens[:3]
        if len(keys) > 1 and starred:
            pre_text = post_text = ''

        cite_template = join(sep=', ')[
            ref(classes=['natbib'])[authors(
                last_names_only=True,
                last_sep=' and ' if starred else ' & ',
                et_al=not starred)],
            ref(classes=['natbib'])[year]
        ]

        groups = get_key_groups(keys, bibcache)

        return join[
            optional[boolean[parenthesis], '('],
            optional[pre_text],
            join(sep='; ')[[
                join(sep=', ')[[
                    ifelse[
                        boolean[i > 0],
                        ref[field['year_suffix']].format(
                            entry=bibcache[key], docname=docname),
                        cite_template.format(
                            entry=bibcache[key], docname=docname)
                    ]
                    for i, key in enumerate(group)
                ]] for group in groups
            ]],
            optional[post_text],
            optional[boolean[parenthesis], ')']].format()

    @staticmethod
    def cite(citenode, docname, bibcache):
        """Cite method for testing."""
        tokens = citenode.data['tokens']
        _, keys, _ = tokens[:3]
        cite_template = join(sep=', ')[
            ref[authors(
                last_names_only=True,
                last_sep=' & ',
                et_al=True)],
            ref[year]
        ]

        output = join(sep='; ')[
            citation_group(keys, bibcache, cite_template, docname)
        ]

        return output.format()


def citation_group(keys, bibcache, cite_template, docname):
    """Create citations for groups of keys."""
    groups = get_key_groups(keys, bibcache)
    template = [
        join(sep=', ')[[
            ifelse[
                boolean[i > 0],
                idem[
                    ref[field['year_suffix']].format(
                        entry=bibcache[key], docname=docname)
                ],
                idem[
                    cite_template.format(
                        entry=bibcache[key], docname=docname)
                ]
            ]
            for i, key in enumerate(group)
        ]] for group in groups
    ]
    return template


def get_key_groups(keys, bibcache):
    """Identify citation contractions if necessary.

    This faciliates, for example:

        Smith 2008a, Smith 2008b -> Smith 2008a,b
    """
    sort_template = join[authors, field['year']]
    groups = OrderedDict()
    for key in keys:
        entry = bibcache[key]
        sort_key = sort_template.format(entry=entry).astext()
        groups[sort_key] = groups.get(sort_key, []) + [key]

    return [groups[key] for key in groups]
