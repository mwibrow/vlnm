import re

from pybtex.style.formatting import BaseStyle, toplevel
from pybtex.style.unsrt import Style as UnsrtStyle
from pybtex.style.template import (
    join, words, together, field, optional, first_of,
    names, sentence, tag, optional_field, href
)
from pybtex.richtext import Text, Symbol


def dashify(text):
    dash_re = re.compile(r'-+')
    return Text(Symbol('ndash')).join(text.split(dash_re))


pages = field('pages', apply_func=dashify)

date = words [optional_field('month'), field('year')]


class Style(BaseStyle):

    def format_names(self, role, as_sentence=True):
        formatted_names = names(role, sep=', ', sep2 = ' and ', last_sep=', and ')
        if as_sentence:
            return sentence [formatted_names]
        else:
            return formatted_names

    def format_author_year(self, e):
        return sentence [
            self.format_names('author'),
            join ['(', field('year'), ')']
        ]

    def format_article(self, e):
        volume_and_pages = first_of [
            # volume and pages, with optional issue number
            optional [
                join [
                    field('volume'),
                    optional['(', field('number'),')'],
                    ':', pages
                ],
            ],
            # pages only
            words ['pages', pages],
        ]
        template = toplevel [
            self.format_author_year(e),
            self.format_title(e, 'title'),
            sentence [
                tag('em') [field('journal')],
                optional[ volume_and_pages ],
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_author_or_editor(self, e):
        return first_of [
            optional[ self.format_names('author') ],
            self.format_editor(e),
        ]

    def format_editor(self, e, as_sentence=True):
        editors = self.format_names('editor', as_sentence=False)
        if 'editor' not in e.persons:
            # when parsing the template, a FieldIsMissing exception
            # will be thrown anyway; no need to do anything now,
            # just return the template that will throw the exception
            return editors
        if len(e.persons['editor']) > 1:
            word = 'editors'
        else:
            word = 'editor'
        result = join(sep=', ') [editors, word]
        if as_sentence:
            return sentence [result]
        else:
            return result

    def format_volume_and_series(self, e, as_sentence=True):
        volume_and_series = optional [
            words [
                together ['Volume' if as_sentence else 'volume', field('volume')], optional [
                    words ['of', field('series')]
                ]
            ]
        ]
        number_and_series = optional [
            words [
                join(sep=Symbol('nbsp')) ['Number' if as_sentence else 'number', field('number')],
                optional [
                    words ['in', field('series')]
                ]
            ]
        ]
        series = optional_field('series')
        result = first_of [
            volume_and_series,
            number_and_series,
            series,
        ]
        if as_sentence:
            return sentence(capfirst=True) [result]
        else:
            return result

    def format_chapter_and_pages(self, e):
        return join(sep=', ') [
            optional [together ['chapter', field('chapter')]],
            optional [together ['pages', pages]],
        ]

    def format_edition(self, e):
        return optional [
            words [
                field('edition', apply_func=lambda x: x.lower()),
                'edition',
            ]
        ]

    def format_title(self, e, which_field, as_sentence=True):
        formatted_title = field(
            which_field, apply_func=lambda text: text.capitalize()
        )
        if as_sentence:
            return sentence [ formatted_title ]
        else:
            return formatted_title

    def format_btitle(self, e, which_field, as_sentence=True):
        formatted_title = tag('em') [ field(which_field) ]
        if as_sentence:
            return sentence[ formatted_title ]
        else:
            return formatted_title

    def format_address_organization_publisher_date(
        self, e, include_organization=True):
        """Format address, organization, publisher, and date.
        Everything is optional, except the date.
        """
        # small difference from unsrt.bst here: unsrt.bst
        # starts a new sentence only if the address is missing;
        # for simplicity here we always start a new sentence
        if include_organization:
            organization = optional_field('organization')
        else:
            organization = None
        return first_of[
            # this will be rendered if there is an address
            optional [
                join(sep=' ') [
                    sentence[
                        field('address'),
                        date,
                    ],
                    sentence[
                        organization,
                        optional_field('publisher'),
                    ],
                ],
            ],
            # if there is no address then we have this
            sentence[
                organization,
                optional_field('publisher'),
                date,
            ],
        ]

    def format_book(self, e):
        template = toplevel [
            self.format_author_or_editor(e),
            self.format_btitle(e, 'title'),
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                self.format_edition(e)
            ],
            optional[ sentence [ self.format_isbn(e) ] ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_booklet(self, e):
        template = toplevel [
            self.format_author_or_editor(e),
            self.format_title(e, 'title'),
            sentence [
                optional_field('howpublished'),
                optional_field('address'),
                optional_field('note'),
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_inbook(self, e):
        template = toplevel [
            self.format_author_or_editor(e),
            sentence [
                self.format_btitle(e, 'title', as_sentence=False),
                self.format_chapter_and_pages(e),
            ],
            self.format_volume_and_series(e),
            sentence [
                field('publisher'),
                optional_field('address'),
                optional [
                    words [field('edition'), 'edition']
                ],
                date,
                optional_field('note'),
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_incollection(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            words [
                'In',
                sentence [
                    optional[ self.format_editor(e, as_sentence=False) ],
                    self.format_btitle(e, 'booktitle', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    self.format_chapter_and_pages(e),
                ],
            ],
            sentence [
                optional_field('publisher'),
                optional_field('address'),
                self.format_edition(e),
                date,
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_inproceedings(self, e):
        template = toplevel [
            self.format_author_year(e),
            self.format_title(e, 'title'),
            words [
                'In',
                sentence [
                    optional[ self.format_editor(e, as_sentence=False) ],
                    self.format_btitle(e, 'booktitle', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    optional[ pages ],
                ],
                self.format_address_organization_publisher_date(e),
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_manual(self, e):
        # TODO this only corresponds to the bst style if author is non-empty
        # for empty author we should put the organization first
        template = toplevel [
            optional [ sentence [ self.format_names('author') ] ],
            self.format_btitle(e, 'title'),
            sentence [
                optional_field('organization'),
                optional_field('address'),
                self.format_edition(e),
                optional[ date ],
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_mastersthesis(self, e):
        template = toplevel [
            self.format_author_year(e),
            self.format_title(e, 'title'),
            sentence[
                "Master's thesis",
                field('school'),
                optional_field('address')
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_misc(self, e):
        template = toplevel [
            optional[ sentence [self.format_names('author')] ],
            optional[ self.format_title(e, 'title') ],
            sentence[
                optional[ field('howpublished') ],
                optional[ date ],
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_phdthesis(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_btitle(e, 'title'),
            sentence[
                'PhD thesis',
                field('school'),
                optional_field('address'),
                date,
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_proceedings(self, e):
        template = toplevel [
            first_of [
                # there are editors
                optional [
                    join(' ')[
                        self.format_editor(e),
                        sentence [
                            self.format_btitle(e, 'title', as_sentence=False),
                            self.format_volume_and_series(e, as_sentence=False),
                            self.format_address_organization_publisher_date(e),
                        ],
                    ],
                ],
                # there is no editor
                optional_field('organization'),
                sentence [
                    self.format_btitle(e, 'title', as_sentence=False),
                    self.format_volume_and_series(e, as_sentence=False),
                    self.format_address_organization_publisher_date(
                        e, include_organization=False),
                ],
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_techreport(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            sentence [
                words[
                    first_of [
                        optional_field('type'),
                        'Technical Report',
                    ],
                    optional_field('number'),
                ],
                field('institution'),
                optional_field('address'),
                date,
            ],
            sentence [ optional_field('note') ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_unpublished(self, e):
        template = toplevel [
            sentence [self.format_names('author')],
            self.format_title(e, 'title'),
            sentence [
                field('note'),
                optional[ date ]
            ],
            self.format_web_refs(e),
        ]
        return template.format_data(e)

    def format_web_refs(self, e):
        # based on urlbst output.web.refs
        return sentence [
            optional [ self.format_url(e) ],
            optional [ self.format_eprint(e) ],
            optional [ self.format_pubmed(e) ],
            optional [ self.format_doi(e) ],
            ]

    def format_url(self, e):
        # based on urlbst format.url
        return words [
            'URL:',
            href [
                field('url', raw=True),
                field('url', raw=True)
                ]
        ]

    def format_pubmed(self, e):
        # based on urlbst format.pubmed
        return href [
            join [
                'https://www.ncbi.nlm.nih.gov/pubmed/',
                field('pubmed', raw=True)
                ],
            join [
                'PMID:',
                field('pubmed', raw=True)
                ]
            ]

    def format_doi(self, e):
        # based on urlbst format.doi
        return href [
            join [
                'https://doi.org/',
                field('doi', raw=True)
                ],
            join [
                'doi:',
                field('doi', raw=True)
                ]
            ]

    def format_eprint(self, e):
        # based on urlbst format.eprint
        return href [
            join [
                'https://arxiv.org/abs/',
                field('eprint', raw=True)
                ],
            join [
                'arXiv:',
                field('eprint', raw=True)
                ]
            ]

    def format_isbn(self, e):
        return join(sep=' ') [ 'ISBN', field('isbn') ]
