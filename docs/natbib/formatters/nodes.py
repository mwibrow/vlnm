"""
    Template language based on pybtex
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
# pylint: disable=C0103,W0621

import docutils.nodes

class Context:
    """Singleton context."""

    _instance = None
    context = {}

    def __new__(cls):
        if cls._instance:
            return cls._instance
        cls._instance = object.__new__(cls)
        return cls._instance

    def __getitem__(self, item):
        return self.context.get(item)

    def update(self, **kwargs):
        """Update the context."""
        self.context.update(kwargs)

    def get(self, key, default):
        """Return an item from the context."""
        if key in self.context:
            return self.context[key]
        return default

    def clear(self):
        """Clear the context."""
        self.context = {}

class Node:
    """Base node class."""

    def __init__(self, text='', **kwargs):
        self.context = Context()
        if isinstance(text, Node):
            self.text = text.text
            self.children = text.children
            self.kwargs = text.kwargs
        else:
            self.text = text
            self.children = []
            self.kwargs = {}
        self.kwargs.update(kwargs)
        self.context.update(**kwargs.get('context', {}))

    def clone(self):
        """Clone this node instance."""
        obj = object.__new__(self.__class__)
        obj.text = self.text
        obj.children = []
        obj.kwargs = self.kwargs
        obj.context = Context()
        return obj

    def append(self, nodes):
        """Append a child to this node."""
        for node in nodes:
            if node:
                self.children.append(node)
        return self

    def transform(self, nodes):
        """Transform this node."""
        nodes = [Node(node) for node in nodes if node]
        self.children.extend(nodes)
        return self

    def __getitem__(self, nodes):
        node = self.clone()
        return node.transform(nodes)

    def __add__(self, node):
        self.append([node])

    def __bool__(self):
        if self.text or self.children:
            return True
        return False

    def __call__(self, **kwargs):
        self.kwargs.update(kwargs)
        self.context.update(**self.kwargs.get('context', {}))
        return self

    def __repr__(self):
        children = ''.join(child.__repr__() for child in self.children)
        if children:
            return '{}'.format(children)
        if self.text:
            return '{}'.format(self.text)
        return ''

    def format(self):
        """Format to docutils nodes."""
        if self.text:
            node = docutils.nodes.inline(self.text, self.text)
        else:
            node = docutils.nodes.inline('', '')
        if self.children:
            for child in self.children:
                node += child.format()
        return node

class TopLevel(Node):
    """Top level node with only one child."""

    def transform(self, nodes):
        """Add the nodes to this nodes' children."""
        self.children.append(nodes)
        return self

class Field(Node):
    """Node for getting fields from the context."""

    def transform(self, nodes):
        """Get the field from the context."""
        item = self.context.get('fields', {}).get(nodes)
        self.text = item
        return self

class Join(Node):
    """Node for joining nodes together."""
    def __init__(self, sep=''):
        super(Join, self).__init__(sep=sep)

    def transform(self, nodes):
        """Join nodes together."""
        nodes = [Node(node) for node in nodes if node]
        for node in nodes[:-1]:
            self.children.append(node)
            self.children.append(Node(self.kwargs['sep']))
        self.children.append(nodes[-1])
        return self

class Optional(Node):
    """Optionally transform node."""

    def transform(self, nodes):
        """If first node is truthy, append the rest of the nodes."""
        condition = nodes[0]
        rest = [Node(node) for node in nodes[1:] if node]
        if condition:
            self.children.extend(rest)
        return self

class Text(Node):
    """Simple text node."""
    def transform(self, nodes):
        self.text = nodes
        return self


toplevel = TopLevel()
field = Field()
join = Join()
words = Join(sep=' ')
optional = Optional()
text = Text()
