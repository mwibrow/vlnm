"""
    Template language based on pybtex
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import inspect
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
        self._called = False

    def add_child(self, child):
        """Add a child to this node."""
        self.children.append(child)

    def clone(self):
        """Clone this node."""
        node = object.__new__(self.__class__)
        node.content = self.content
        node.children = []
        node.classes = self.classes
        if self._called:
            node.kwargs = self.kwargs
        else:
            node.kwargs = {}
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
        node = self.clone()
        node.kwargs.update(kwargs)
        node._called = True  # pylint: disable=protected-access
        return node

    def __getitem__(self, items):
        if self._called:
            node = self
        else:
            node = self.clone()
        if not isinstance(items, tuple):
            items = (items,)
        return node.transform(items)

    def __repr__(self):
        node = '{}{}'.format(
            self.__class__.__name__,
            '(\'{}\')'.format(self.content) if self.content else '')
        children = ', '.join(to_repr(child) for child in self.children)
        if children:
            children = '[{}]'.format(children)
        return '{}{}'.format(node, children)

    def __iter__(self):
        yield self

def to_repr(obj):
    """Convert to string representation."""
    if inspect.isfunction(obj):
        return '{}()'.format(obj.__name__)
    return obj.__repr__()

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
            return docutils.nodes.inline(value, value, classes=[self.content])
        except (AttributeError, KeyError):
            return None

class Join(Node):
    """Node class for joining nodes."""

    def transform(self, items):
        """Transform this node instance."""
        for item in items:
            if item:
                if isinstance(item, list):
                    self.transform(item)
                else:
                    if isinstance(item, str):
                        item = Text(item)
                    self.add_child(item)
        return self

    def format(self, **kwargs):
        """Format this node."""
        parent = kwargs.get('parent') or docutils.nodes.inline('', '')
        sep = self.kwargs.get('sep')
        last_sep = self.kwargs.get('last_sep')
        children = []
        for child in self.children:
            for element in child:
                element = format_node(element, **kwargs)
                if element:
                    children.append(element)
        for i, child in enumerate(children[:-1]):
            parent += child
            if i < len(children) - 2:
                if sep:
                    parent += docutils.nodes.inline(sep, sep)
            else:
                current_sep = sep or last_sep
                if current_sep:
                    parent += docutils.nodes.inline(current_sep, current_sep)
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
            if len(self.children) == 1:
                parent += condition
                return parent
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
        return self

    def format(self, **kwargs):
        """Format this node."""
        func = self.children[0]
        args = [child for child in self.children[1:]]
        output = func(*args)
        return docutils.nodes.inline(output, output)

class Boolean(Node):
    def transform(self, items):
        """Transform this node instance."""
        self.content = items
        return self

    def format(self, **kwargs):
        if self.content[0]:
            return True
        return False

class Sentence(Node):
    def transform(self, items):
        """Transfor this node instance."""
        self.children = items
        return self

    def format(self, **kwargs):
        """Format this node instance."""
        nodes = join[self.children, '. '].format(**kwargs)
        original = nodes.traverse(condition=docutils.nodes.Text)[0]
        replacement = docutils.nodes.inline(
            original.capitalize(),
            original.capitalize())
        original.parent.replace_self(replacement)
        return nodes

class Words(Node):
    """Word node class."""
    def transform(self, items):
        """Transfor this node instance."""
        self.children = items
        return self

    def format(self, **kwargs):
        """Format this node instance."""
        return join(sep=' ')[self.children].format(**kwargs)

# pylint: disable=C0103
call = Call()
emph = Emph()
field = Field()
join = Join()
optional = Optional()
text = Text()
boolean = Boolean()
sentence = Sentence()
words = Words()
