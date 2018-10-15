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
        """Add a child to this node."""
        self.children.append(child)

    def clone(self):
        """Clone this node."""
        node = object.__new__(self.__class__)
        node.content = self.content
        node.children = []
        node.classes = self.classes
        node.kwargs = self.kwargs
        return node

    def transform(self, _items):
        """Transform this node."""
        return self

    def format(self, **kwargs):
        """Format this node to a docutils node."""
        self.kwargs.update(**kwargs)
        return docutils.nodes.inline(
            self.content,
            self.content,
            classes=self.classes)

    def __add__(self, child):
        self.add_child(Node(child))
        return self

    def __bool__(self):
        if self.content or self.children:
            return True
        return False

    def __call__(self, **kwargs):
        self.kwargs.update(kwargs)
        return self

    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = (items,)
        self.transform(items)

    def __repr__(self):
        node = '{}{}'.format(
            self.__class__.__name__,
            '(\'{}\')'.format(self.content) if self.content else '')
        children = ', '.join(child.__repr__() for child in self.children)
        if children:
            children = '[{}]'.format(children)
        return '{}{}'.format(node, children)


class Text(Node):
    """Text node."""
    def transform(self, items):
        """Transform this node instance."""
        self.content = items[0]
        return self

class Emph(Text):
    """Text node with emphasis."""
    def format(self, **kwargs):
        """Format this node to a docutils node."""
        self.kwargs.update(kwargs)
        return docutils.nodes.emphasis(
            self.content,
            self.content,
            classes=self.classes)

class Field(Node):
    """Node class for obtaining fields."""
    def transform(self, items):
        """Transform this node instance."""
        self.content = items[0]
        return self

    def format(self, **kwargs):
        try:
            value = kwargs.get('entry').fields[self.content]
            return value
        except (AttributeError, KeyError):
            return None

class Join(Node):
    """Node class for joining nodes."""
    def transform(self, items):
        """Transform this node instance."""
        for item in items:
            if item:
                self.add_child(item)

    def format(self, **kwargs):
        return


field = Field()
emph = Emph()
join = Join()
text = Text()

join[ '(', field['year']]