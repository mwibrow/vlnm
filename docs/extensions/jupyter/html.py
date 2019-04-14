"""
    Module for generating raw HTML.
"""
# pylint: disable=invalid-name


class Tag:

    def __init__(self, tag=None, content='', classes=None, attributes=None):
        self.tag = tag or self.__class__.__name__
        self.content = content
        self.classes = classes or []
        self.children = []
        self.attributes = attributes or []

    def add_child(self, tag):
        if isinstance(tag, list):
            self.children.extend(tag)
        else:
            self.children.append(tag)
        return self

    def __add__(self, tag):
        self.add_child(tag)
        return self

    def to_html(self):
        tag = self.tag
        if self.children:
            content = '\n'.join(child.to_html() for child in self.children)
        else:
            content = self.content
        if self.classes:
            klasses = ' class="{}"'.format(' '.join(self.classes))
        else:
            klasses = ''
        if self.attributes:
            attributes = ' {}'.format(
                ' '.join(
                    '{}={}'.format(name, value)
                    for name, value in self.attributes.items()))
        else:
            attributes = ''
        html = '<{}{}{}>\n{}</{}>'.format(
            tag, klasses, attributes, content, tag)
        print(html)
        return html

    def __repr__(self):

        return self.to_html()


class table(Tag):
    pass


class thead(Tag):
    pass


class tbody(Tag):
    pass


class tr(Tag):
    pass


class th(Tag):
    pass


class td(Tag):
    pass


class Float64:

    @staticmethod
    def th(column):
        tag = th(
            content=column,
            classes=['column-{}'.format(column), 'column-dtype-float64'],
            attributes={
                'colspan': 2,
                'style': '"text-align: center;"'})
        return tag

    @staticmethod
    def td(value, formatter=None):
        if formatter:
            value = formatter.format(value)
        integer, mantissa = str(value).split('.')
        return [
            td(
                content=integer,
                classes=[],
                attributes={
                    'style': '"text-align: right; padding-right: 0;"'
                }),
            td(
                content='.{}'.format(mantissa),
                classes=[],
                attributes={
                    'style': '"text-align: left; padding-left: 0;"'
                })
        ]


dtypes = {
    'float64': Float64
}
