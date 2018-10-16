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
        node = self.clone()
        if not isinstance(items, tuple):
            items = (items,)
        return node.transform(items)

    def __repr__(self):
        node = '{}{}'.format(
            self.__class__.__name__,
            '(\'{}\')'.format(self.content) if self.content else '')
        children = ', '.join(child.__repr__() for child in self.children)
        if children:
            children = '[{}]'.format(children)
        return '{}{}'.format(node, children)

    def __iter__(self):
        yield self

def format_node(node, **kwargs):
    """Helper for formatting nodes."""
    try:
        return node.format(**kwargs)
    except AttributeError:
        return node(**kwargs)

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
                if isinstance(item, str):
                    item = Text(item)
                self.add_child(item)
        return self

    def format(self, **kwargs):
        """Format this node."""
        parent = kwargs.get('parent') or docutils.nodes.inline('', '')
        sep = self.kwargs.get('sep')
        children = []
        for child in self.children:
            child = format_node(child, **kwargs)
            if child:
                children.append(child)
        for child in children[:-1]:
            parent += child
            if sep:
                parent += docutils.nodes.inline(sep, sep)
        parent += children[-1]
        return parent


class Optional(Node):
    """Node class for optional nodes."""
    def transform(self, items):
        """Transform this node instance."""
        for item in items:
            if item:
                if isinstance(item, str):
                    item = Text(item)
                self.add_child(item)
        return self

    def format(self, **kwargs):
        """Format this node."""
        condition = self.children[0].format(**kwargs)
        if condition:
            parent = kwargs.get('parent') or docutils.nodes.inline('', '')
            for child in self.children[1:]:
                child = format_node(child, **kwargs)
                if child:
                    parent += child
            return parent
        return None

class Call(Node):
    """Node class for wrapping functions."""
    def transform(self, items):
        """Transform this node instance."""
        self.children = items

    def format(self, **kwargs):
        """Format this node."""
        func = self.children[0]
        args = [format_node(child, **kwargs) for child in self.children[1:]]
        return func(**args)

# pylint: disable=C0103
call = Call()
emph = Emph()
field = Field()
join = Join()
optional = Optional()
text = Text()
