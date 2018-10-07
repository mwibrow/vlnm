import docutils.nodes

def latex_decode(text):
    """
    Decode ascii text latex formant to UTF-8
    """
    return text.encode('ascii').decode('latex')

class ApaStyle:
    """
    Class for creating citations and bibliographic entries in the APA style.
    """
    def __init__(self):
        self.nodes = []
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
            ]
        }

    def get_authors(self, authors, **kwargs):
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
            author_node = docutils.nodes.inline(text, text)
            author_node['classes'].append('author')
            nodes.append(author_node)

            if len(authors) == 2 and i == 0:
                nodes.append(docutils.nodes.inline(' & ', ' & '))
        return nodes

    def get_editor(self, editor, **kwargs):
        nodes = kwargs.get('nodes') or self.nodes or []
        if editor:
            nodes.append(docutils.nodes.inline('In ', 'In '))
            self.get_authors(editor, nodes=nodes)
            nodes.append(docutils.nodes.inline(' (eds), ', ' (eds), '))
        return nodes


    def get_pages(self, pages, **kwargs):
        nodes = kwargs.get('nodes') or self.nodes or []
        if pages:
            nodes.extend([
                docutils.nodes.inline('pp', 'pp'),
                docutils.nodes.inline(pages, pages),
                docutils.nodes.inline('. ', '. ')])
        return nodes

    def get_volume(self, volume, **kwargs):
        """Get publication volume"""
        nodes = kwargs.get('nodes') or self.nodes or []
        fields = kwargs.get('fields', {})
        if volume:
            nodes.append(docutils.nodes.inline('Vol. ', 'Vol. '))
            nodes.append(docutils.nodes.inline(volume, volume))
            if fields.get('number'):
                nodes.append(docutils.nodes.inline(' ', ' '))
            else:
                nodes.append(docutils.nodes.inline('. ', '. '))
        return nodes

    def get_number(self, number, **kwargs):
        """Get publication number"""
        nodes = kwargs.get('nodes') or self.nodes or []
        if number:
            nodes.append(docutils.nodes.inline('No. ', 'No. '))
            nodes.append(docutils.nodes.inline(number, number))
            nodes.append(docutils.nodes.inline('. ', '. '))
        return nodes

    def get_year(self, year, **kwargs):
        nodes = kwargs.get('nodes') or self.nodes or []
        if year:
            year = latex_decode(year)
            nodes.append(
                docutils.nodes.inline(year, ' ({})'.format(year), classes=['year']))
            nodes.append(docutils.nodes.inline('. ', '. '))
        return nodes

    def get_title(self, title, **kwargs):
        nodes = kwargs.get('nodes') or self.nodes or []
        if title:
            nodes.append(docutils.nodes.inline(title, title, classes=['title']))
            nodes.append(docutils.nodes.inline('.  ', '.  '))
        return nodes

    def get_booktitle(self, booktitle, **kwargs):
        nodes = kwargs.get('nodes') or self.nodes or []
        fields = kwargs.get('fields' or {})
        if booktitle:
            title = latex_decode(booktitle)
            nodes.append(docutils.nodes.emphasis(
                title, title, classes=['publication']))
            if fields.get('volume'):
                nodes.append(docutils.nodes.inline(', ', ', '))
            else:
                nodes.append(docutils.nodes.inline('. ', '. '))
        return nodes

    def get_journal(self, journal, **kwargs):
        return self.get_booktitle(journal, **kwargs)

    def get_nodes(self, ref):
        publication = self.publications[ref.type]
        ref_node = docutils.nodes.paragraph('', '', classes=[ref.type, 'reference'])
        ref_fields = ref.fields
        for field in publication:
            if field == 'authors':
                source = ref.persons.get('author', [])
            elif field == 'editor':
                source = ref.persons.get('editor', [])
            else:
                source = ref.fields.get(field)
            getter = 'get_{}'.format(field)
            if hasattr(self, getter):
                nodes = getattr(self, getter)(source, fields=ref_fields)
                for node in nodes:
                    ref_node += node
        return ref_node

    def make_entry(self, ref):
        publication = self.publications[ref.type]
        self.nodes = []
        ref_node = docutils.nodes.paragraph('', '', classes=[ref.type, 'reference'])
        ref_fields = ref.fields
        for field in publication:
            if field == 'authors':
                source = ref.persons.get('author', [])
            elif field == 'editor':
                source = ref.persons.get('editor', [])
            else:
                source = ref.fields.get(field)
            getter = 'get_{}'.format(field)
            if hasattr(self, getter):
                nodes = getattr(self, getter)(source, fields=ref_fields)
                for node in nodes:
                    ref_node += node
        return ref_node

    def make_citation(self, bibnode, bibcache, make_refid):
        node = docutils.nodes.inline('', '')
        classes = ['xref', 'cite']
        typ = bibnode.data['typ']
        keys = bibnode.data['keys']
        pre_text = bibnode.data.get('pre_text')
        post_text = bibnode.data.get('post_text')

        if typ in ['citep', 'citealp']:
            if typ != 'citealp':
                node += docutils.nodes.inline('(', '(')
            if pre_text:
                text = '{} '.format(pre_text)
                node += docutils.nodes.inline(text, text)
            for i, key in enumerate(keys):
                entry = bibcache[key]
                refid = make_refid(entry, bibnode.data['docname'])

                authors = entry.persons.get('author')
                text = ''
                if len(authors) == 1:
                    text = authors[0].last()[0]
                elif len(authors) == 2:
                    names = [name.last()[0] for name in authors]
                    text += ' & '.join(names)

                refnode = docutils.nodes.reference(
                    text, text, internal=True, refuri='#{}'.format(refid),
                    classes=classes)
                node += refnode

                year = entry.fields.get('year')
                if year:
                    node += docutils.nodes.inline(', ', ', ')
                    refnode = docutils.nodes.reference(
                        year, year, internal=True, refuri='#{}'.format(refid),
                        classes=classes)
                    node += refnode

                if len(keys) > 1:
                    if i < len(keys) - 1:
                        node += docutils.nodes.inline(', ', ', ')
            if post_text:
                node += docutils.nodes.inline(', ', ', ')
                text = ' {}'.format(post_text)
                node += docutils.nodes.inline(text, text)
            if typ != 'citealp':
                node += docutils.nodes.inline(')', ')')

        if typ in ['citet']:
            for key in keys:
                entry = bibcache[key]
                refid = make_refid(entry, bibnode.data['docname'])

                authors = entry.persons.get('author')
                text = ''
                if len(authors) == 1:
                    text = authors[0].last()[0]
                elif len(authors) == 2:
                    names = [name.last()[0] for name in authors]
                    text += ' & '.join(names)

                refnode = docutils.nodes.reference(
                    text, text, internal=True, refuri='#{}'.format(refid),
                    classes=classes)
                node += refnode

                year = entry.fields.get('year')
                if year:
                    node += docutils.nodes.inline(' (', ' (')
                    if pre_text:
                        text = '{} '.format(pre_text)
                        node += docutils.nodes.inline(text, text)

                    refnode = docutils.nodes.reference(
                        year, year, internal=True, refuri='#{}'.format(refid),
                        classes=classes)
                    node += refnode
                    if post_text:
                        text = ' {}'.format(post_text)
                        node += docutils.nodes.inline(text, text)
                    node += docutils.nodes.inline(')', ')')

        return node
