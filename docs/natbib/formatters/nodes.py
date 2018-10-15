"""
    Template language based on pybtex
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import docutils.nodes

class Node:
    """Based node class."""

    def __init__(self, content=None, children=None, classes=None, **kwargs):
        if isinstance(content, Node):
            node = content
            self.content = node.content
            self.children = children or []
            self.classes = list(set(node.classes + (classes or [])))
            self.kwargs = kwargs
        else:
            self.content = content or ''
            self.children = children or []
            self.classes = classes or []
            self.kwargs = kwargs

    def add_child(self, child):
        self.children.append(child)

    def clone(self):
        """Clone this node."""
        node = object.__new__(self.__class__)
        node.content = self.content
        node.children = []
        node.classes = self.classes
        node.kwargs = kwargs
        return node

    def transform(self, items):
        """Transform this node."""
        return self

    def __add__(self, child):
        self.add_child(Node(child))
        return self

    def __call__(self, **kwargs):
        self.kwargs.update(kwargs)
        return self

    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = (items,)
        self.transform(items)

    def __repr__(self):
        node = '{}{}'.format(
            self.__class__.__name,
            '(\'{}\')'.format(self.content) if self.content else '')
        children = ', '.join(child.__repr__() for child in self children)
        if children:
            children = '[{}]'.format(children)
        return '{}{}'.format(node, children)


class Text(Node):

    def transform(self):
        return docutils.inline()
