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
                    for name, value in self.attributes.values()))
        else:
            attributes = ''
        return '<{}{}{}>\n{}</{}>'.format(
            tag, klasses, attributes, content, tag)

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
