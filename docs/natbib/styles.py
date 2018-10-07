import docutils.nodes

def latex_decode(text):
    """
    Decode ascii text latex formant to UTF-8
    """
    return text.encode('ascii').decode('latex')

class ApaStyle:

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
