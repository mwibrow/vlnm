"""
    Module defining a small template language for creating styles.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import docutils.nodes

class Context:
    """
    Singleton context.
    """
    _instance = None

    def __new__(cls):
        Context._instance = Context._instance or object.__new__(cls)
        return Context._instance

    def __init__(self):
        self.context = {}

    def __getitem__(self, item):
        return self.context.get(item)

    def update(self, **kwargs):
        """Update the context."""
        self.context.update(kwargs)

    def get(self, key, default):
        """Return a key from the context."""
        if key in self.context:
            return self.context[key]
        return default

class Node:
    """
    Template node class.

    Based on pybtex but without the tiresome decorators.
    """
    def __init__(self, node='', **kwargs):
        self.context = Context()
        if isinstance(node, Node):
            self.node = node.node
            self.children = node.children
            self.kwargs = node.kwargs
        else:
            self.node = node
            self.children = []
            self.kwargs = {}
        self.kwargs.update(kwargs)
        self.context.update(**kwargs.get('context', {}))

    def clone(self):
        """Clone this node."""
        obj = object.__new__(self.__class__)
        obj.node = self.node
        obj.children = []
        obj.kwargs = self.kwargs
        obj.context = self.context
        return obj

    def append(self, nodes):
        """Append a node to this node's children."""
        for node in nodes:
            if node:
                self.children.append(node)
        return self

    def transform(self, _nodes):
        """Transform a node."""
        return self

    def __getitem__(self, nodes):
        node = self.clone()
        return node.transform(nodes)

    def __add__(self, node):
        self.append([node])

    def __bool__(self):
        if self.node or self.children:
            return True
        return False

    def __call__(self, **kwargs):
        self.kwargs.update(kwargs)
        self.context.update(**self.kwargs.get('context', {}))
        return self

    def __repr__(self):
        children = ''.join(str(child) for child in self.children)
        if children:
            return '{}'.format(children)
        if self.node:
            return '{}'.format(self.node)
        return ''

    def format(self):
        """Format to docutils nodes."""
        if self.node:
            node = docutils.nodes.inline(self.node, self.node)
        else:
            node = docutils.nodes.inline('', '')
        if self.children:
            for child in self.children:
                node += child.format()
        return node

class TopLevel(Node):
    """Top level node expected to have one child."""
    def transform(self, node):
        self.children.append(node)
        return self

class Field(Node):
    """Node for obtaining fields from the context."""
    def transform(self, node):
        item = self.context.get('fields', {}).get(node)
        self.node = item
        return self

class Join(Node):
    """Node for joining other nodes."""
    def __init__(self, sep=', '):
        super(Join, self).__init__(sep=sep)

    def transform(self, nodes):
        nodes = [Node(node) for node in nodes if node]
        for node in nodes[:-1]:
            self.children.append(node)
            self.children.append(Node(self.kwargs['sep']))
        self.children.append(nodes[-1])
        return self

class Optional(Node):
    """Node for adding optional content."""
    def transform(self, nodes):
        condition = nodes[0]
        rest = nodes = [Node(node) for node in nodes[1:] if node]
        if condition:
            self.children.extend(rest)
        return self

class Text(Node):
    """Add a simple text node."""
    def transform(self, nodes):
        self.node = nodes
        return self

    def format(self):
        """Format to docutils nodes."""
        return docutils.nodes.Text(self.node)
