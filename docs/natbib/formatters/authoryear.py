"""
    New Formatters
    ~~~~~~~~~~~~~~
"""
import re

import docutils.nodes
from docutils.nodes import emphasis, inline, reference

from .formatters import Formatter

def text(content):
    return inline(content, content)

def latex_decode(text):
    """
    Decode ascii text latex formant to UTF-8
    """
    return text.encode('ascii').decode('latex').replace(
        '\\:{o}', 'ö')

def dashify(text, dash='–'):
    """Replace dashes with unicode dash."""
    return re.sub(r'-+', dash, text)

class AuthorYearFormatter(Formatter):
    """
    Class for creating citations and bibliographic entries in the APA style.
    """
    def __init__(self):
        super(AuthorYearFormatter, self).__init__()
        self.nodes = []
        self.entry = None
        self.publications = {
            'article': [
                'authors',
                'year',
                'title',
                'journal',
                'volume',
                'number',
                'pages',
                'doi',
            ],
            'inproceedings': [
                'authors',
                'year',
                'title',
                'editor',
                'booktitle',
                'publisher',
                'volume',
                'number',
                'pages'
            ],
            'incollection': [
                'authors',
                'year',
                'title',
                'editor',
                'booktitle',
                'publisher',
                'volume',
                'number',
                'pages'
            ],
            'phdthesis': [
                'authors',
                'year',
                'title',
                inline('PhD Dissertation. ', 'PhD Dissertation. '),
                'school'
            ]
        }

    @staticmethod
    def sort_keys(keys, bibcache):
        """
        Return a sort key for sorting the bibliography
        """
        def _sort_key(key):
            return bibcache[key].persons.get('author')[0].last()[0]
        return sorted(keys, key=_sort_key)

    def get_authors(self, authors, **kwargs):
        """
        Get the author node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        for i, author in enumerate(authors):
            text = ' '.join(latex_decode(name) for name in author.last())

            if author.first() or author.middle():
                names = [author.first(), author.middle()]
                text += ', '
                for name in names:
                    parts = [part for part in name if part]
                    text += ' '.join(
                        '{}. '.format(latex_decode(part)[0].upper())
                        for part in parts)

            text = text.strip()
            author_node = inline(text, text)
            author_node['classes'].append('author')
            nodes.append(author_node)

            if len(authors) > 1 and i < len(authors) - 1:
                if i == len(authors) - 2:
                    nodes.append(inline(' & ', ' & '))
                else:
                    nodes.append(inline(', ', ', '))


        return nodes

    def get_editor(self, editor, **kwargs):
        """
        Get the editor node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        if editor:
            nodes.append(inline('In ', 'In '))
            self.get_authors(editor, nodes=nodes)
            nodes.append(inline(' (eds), ', ' (eds), '))
        return nodes


    def get_pages(self, pages, **kwargs):
        """
        Get the pages node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        if pages:
            pages = dashify(pages)
            nodes.extend([
                inline(pages, pages),
                inline('. ', '. ')])
        return nodes

    def get_volume(self, volume, **kwargs):
        """
        Get the volume node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        fields = kwargs.get('fields', {})
        if volume:
            nodes.append(inline(volume, volume))
            if fields.get('number'):
                pass
            elif fields.get('pages'):
                nodes.append(inline(', ', ', '))
            else:
                nodes.append(inline('. ', '. '))
        return nodes

    def get_number(self, number, **kwargs):
        """
        Get the number node for a bibliographic entry.
        """
        fields = kwargs.get('fields', {})
        nodes = kwargs.get('nodes') or self.nodes or []
        if number:
            nodes.extend([
                inline('(', '('),
                inline(number, number),
                inline(')', ')')])
            if fields.get('pages'):
                nodes.append(inline(', ', ', '))
            else:
                nodes.append(inline('. ', '. '))
        return nodes

    def get_year(self, year, **kwargs):
        """
        Get the year node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        if year:
            year = latex_decode(year)
            nodes.append(
                inline(
                    year, ' ({})'.format(year), classes=['year']))
            nodes.append(inline('. ', '. '))
        return nodes

    def get_title(self, title, **kwargs):
        """
        Get the title node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        ref_type = kwargs.get('type')
        if title:
            node = emphasis if ref_type == 'phdthesis' else inline
            print(ref_type)
            nodes.append(node(title, title, classes=['title']))
            nodes.append(inline('.  ', '.  '))
        return nodes

    def get_booktitle(self, booktitle, **kwargs):
        """
        Get the booktitle node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        fields = kwargs.get('fields' or {})
        if booktitle:
            title = latex_decode(booktitle)
            nodes.append(emphasis(
                title, title, classes=['publication']))
            if fields.get('volume'):
                nodes.append(inline(', ', ', '))
            else:
                nodes.append(inline('. ', '. '))
        return nodes

    def get_journal(self, journal, **kwargs):
        """
        Get the journal node for a bibliographic entry.
        """
        return self.get_booktitle(journal, **kwargs)

    def get_school(self, school, **kwargs):
        """
        Get the journal node for a bibliographic entry.
        """
        nodes = kwargs.get('nodes') or self.nodes or []
        nodes.extend([
            inline(school, school),
            inline('.', '.')
        ])
        return nodes

    def get_doi(self, doi, **kwargs):
        """Get the doi."""
        nodes = kwargs.get('nodes') or self.nodes or []
        if not doi:
            return []
        doi_text = 'doi: {}'.format(doi)
        nodes.extend([
            reference(doi_text, doi_text, internal=False, refuri='https://doi.org/{}'.format(doi))
        ])
        return nodes

    def format_person(self, person, person_type='author'):
        node = inline('', '', classes=[person_type])
        for part in name_part(person.rich_prelast_names, after=' ', sep=' ', abbr=False):
            node += part
        for part in name_part(person.rich_last_names, abbr=False):
            node += part
        for part in name_part(person.rich_first_names, before=', ', sep=' ', abbr=True):
            node += part
        return node

    def format_authors(self, entry, parent):
        authors = entry.persons['author']
        node = inline('', '', classes=['authors'])
        for i, author in enumerate(authors):
            node += self.format_person(author)
            if len(authors) > 1:
                if i == len(authors) - 2:
                    node += text(' and ')
                elif i < len(authors) - 1:
                    node += text(', ')
        return node

    def format_year(self, entry):
        node = inline('', classes=['year'])
        node += text('(') + text(entry.fields['year']) + text(')')
        return node

    def format_title(self, entry):
        node = inline('', classes=['title'])
        node += text(entry.fields['title']) + text('. ')
        return node

    def format_journal(self, entry):
        node = inline('', classes=['journal'])
        node += emphasis(entry.fields['journal'], entry.fields['journal'])
        return node

    def format_volume_and_number(self, entry):
        node = inline('', classes=['volume'])
        volume = entry.fields.get('volume')
        number = entry.fields.get('number')
        node += text(volume)
        if number:
            node += text('(') + text(number) + text(')')
        return node

    def format_pages(self, entry):
        node = inline('', classes=['pages'])
        node += text(dashify(entry.fields.get('pages')))
        return node

    def format_article(self, entry, parent):
        """Format article entry."""
        parent += self.format_authors(entry, parent)
        parent += text(' ')
        parent += self.format_year(entry) + text('. ')
        parent += self.format_title(entry)
        parent += self.format_journal(entry)
        parent += text(', ') + self.format_volume_and_number(entry)
        parent += text(', ') + self.format_pages(entry) + text('.')

    def make_entry(self, ref):
        """
        Make a bibliographic entry.
        """
        self.entry = ref
        getter = 'format_{}'.format(ref.type)
        if hasattr(self, getter):
            ref_node = docutils.nodes.paragraph(
                '', '', classes=[ref.type, 'reference'])
            node = getattr(self, getter)(ref, ref_node)
            if node:
                ref_node += node
            return ref_node

        publication = self.publications[ref.type]
        self.nodes = []
        ref_node = docutils.nodes.paragraph(
            '', '', classes=[ref.type, 'reference'])
        ref_fields = ref.fields
        for field in publication:
            try:
                if field == 'authors':
                    source = ref.persons.get('author', [])
                elif field == 'editor':
                    source = ref.persons.get('editor', [])
                else:
                    source = ref.fields.get(field)
                getter = 'get_{}'.format(field)
                if hasattr(self, getter):
                    nodes = getattr(self, getter)(source, fields=ref_fields, type=ref.type)
                    for node in nodes:
                        ref_node += node
            except AttributeError:
                ref_node += field
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

def name_part(part, before=None, after=None, sep=None, abbr=False):
    if part:
        if before:
            yield text(before)
        for i, subpart in enumerate(part):
            if abbr:
                yield text(subpart.abbreviate().render_as('text'))
            else:
                yield text(subpart.render_as('text'))
            if i < len(part) - 1 and sep:
                yield text(sep)
        if after:
            yield text(after)


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
