"""
    Template language based on pybtex
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import inspect
import docutils.nodes


class Node:
    """Based node class."""

    def __init__(self, content=None, children=None, classes=None, **kwargs):
        self.called = False
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
        node.called = self.called
        if self.called:
            node.kwargs = self.kwargs
        else:
            node.kwargs = {}
        return node

    def template(self, items):
        """Transform this node."""
        self.children = items
        return self

    def format(self, **_kwargs):
        """Format this node to a docutils node."""
        return formatted_node(
            docutils.nodes.inline,
            self.content,
            classes=self.kwargs.get('classes', []))

    def __add__(self, child):
        self.add_child(Node(child))
        return self

    def __bool__(self):
        if self.content or self.children:
            return True
        return False

    def __call__(self, classes=None, **kwargs):
        node = self.clone()
        node.classes = classes or []
        node.kwargs.update(kwargs)
        node.called = True  # pylint: disable=protected-access
        return node

    def __getitem__(self, items):
        if self.called:
            node = self
        else:
            node = self.clone()
        if not isinstance(items, tuple):
            items = (items,)
        return node.template(items)

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


def formatted_node(klass, content, rawsource=None, classes=None, **kwargs):
    """Create a formatted node."""
    klass = kwargs.get('klass', klass)
    if classes:
        return klass(content, rawsource or content, classes=classes)
    return klass(content, rawsource or content)


def to_repr(obj):
    """Convert to representation."""
    if inspect.isfunction(obj):
        return '{}()'.format(obj.__name__)
    return obj.__repr__()


def format_node(node, **kwargs):
    """Helper for formatting nodes."""
    if isinstance(node, str):
        return Text()[node].format()
    try:
        value = node.format(**kwargs)
        if isinstance(value, str):
            value = format_node(value)
    except AttributeError:
        try:
            value = node(**kwargs)
        except TypeError:
            return node
    return value


def child_iterator(children):
    """Iterate over children, replacing strings with nodes."""
    for child in children:
        if isinstance(child, str):
            yield Text()[child]
        elif isinstance(child, list):
            for grandchild in child_iterator(child):
                yield grandchild
        else:
            yield child


class Text(Node):
    """Text node."""

    def template(self, items):
        """Transform this node instance."""
        self.content = items[0]
        return self

    def format(self, **_kwargs):
        """Format this node."""
        return formatted_node(
            docutils.nodes.Text,
            self.content)


class InLine(Node):
    """Inline node."""

    def format(self, **kwargs):
        node = formatted_node(
            docutils.nodes.inline,
            '',
            classes=self.kwargs.get('classes'))
        for child in child_iterator(self.children):
            child = format_node(child, **kwargs)
            if child:
                node += child
        return node


class Emph(Node):
    """Node class for adding emphases"""

    def format(self, **kwargs):
        node = formatted_node(
            docutils.nodes.emphasis,
            '',
            classes=self.kwargs.get('classes'))
        for child in child_iterator(self.children):
            child = format_node(child, **kwargs)
            if child:
                node += child
        return node


class Field(Node):
    """Node class for obtaining fields."""

    def template(self, items):
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

    def template(self, items):
        """Transform this node instance."""
        for item in items:
            if item:
                if isinstance(item, list):
                    self.template(item)
                else:
                    if isinstance(item, str):
                        item = Text(item)
                    self.add_child(item)
        return self

    def format(self, **kwargs):
        """Format this node."""
        parent = kwargs.get('parent')
        if parent is None:
            parent = (
                docutils.nodes.inline('', '', classes=self.classes)
                if self.classes else docutils.nodes.inline('', ''))
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
                current_sep = last_sep or sep
                if current_sep:
                    parent += docutils.nodes.inline(current_sep, current_sep)
        if children:
            parent += children[-1]
        return parent


class Optional(Node):
    """Node class for optional nodes."""

    def template(self, items):
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

    def template(self, items):
        """Transform this node instance."""
        self.children = items
        return self

    def format(self, **kwargs):
        """Format this node."""
        func = self.children[0]
        args = [child.format(**kwargs) for child in self.children[1:]]
        output = func(*args)
        return docutils.nodes.inline(output, output)


class Boolean(Node):
    """Boolean node."""

    def template(self, items):
        """Transform this node instance."""
        self.content = items
        return self

    def format(self, **_kwargs):
        if self.content[0]:
            return True
        return False


class IfElse(Node):
    """If-else node."""

    def template(self, items):
        """Transform this node instance."""
        self.children = items
        return self

    def format(self, **kwargs):
        if format_node(self.children[0], **kwargs):
            return format_node(self.children[1], **kwargs)
        if len(self.children) > 2:
            return format_node(self.children[2], **kwargs)
        return None


class Apply(Node):
    """Apply node."""

    def format(self, **kwargs):
        template = self.children[0]
        return [template[child].format(**kwargs) for child in self.children[1:]]


class Sentence(Node):
    """Sentence node."""

    def template(self, items):
        """Transform this node instance."""
        for item in items:
            if item:
                if isinstance(item, list):
                    self.template(item)
                else:
                    if isinstance(item, str):
                        item = Text(item)
                    self.add_child(item)
        self.add_child(InLine()['.'])
        return self

    def format(self, **kwargs):
        """Format this node instance."""
        self.kwargs.update(sep=' ', last_sep=' ')
        parent = kwargs.get('parent') or docutils.nodes.inline('', '')
        sep = ' '
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
        parent += children[-1]
        return parent


class Words(Node):
    """Word node class."""

    def template(self, items):
        """Transfor this node instance."""
        self.children = items
        return self

    def format(self, **kwargs):
        """Format this node instance."""
        return join(sep=' ')[self.children].format(**kwargs)


class Reference(Node):
    """Reference node class."""

    def format(self, **kwargs):
        """Format this node instance."""
        entry = kwargs.get('entry')
        docname = kwargs.get('docname')
        if entry and docname:
            refuri = '{}#{}'.format(
                '' if docname == 'index' else docname, entry.key)
            ref_node = docutils.nodes.reference(
                '', '', classes=['xref cite'] + self.classes, internal=True, refuri=refuri)
        else:
            ref_node = docutils.nodes.reference(
                '', '', classes=['xref cite'] + self.classes, **self.kwargs)

        ref_node += join[self.children].format(**kwargs)
        return ref_node


class Idempotent(Node):
    """Idempotent Node for a single childe."""

    def template(self, items):
        """Transform this node instance."""
        self.children = items
        return self

    def format(self, **_kwargs):
        """Format this node instance."""
        return self.children[0]


class Link(Node):
    """LinkNode."""

    def format(self, **kwargs):
        """Format this node instance."""
        uri = self.children[0].format(**kwargs).astext()
        if len(self.children) > 1:
            link_text = self.children[1].format(**kwargs).astext()
        else:
            link_text = uri
        ref_node = docutils.nodes.reference(
            link_text, link_text, classes=['xref'] + self.classes, internal=False, refuri=uri)
        return ref_node


# pylint: disable=C0103
boolean = Boolean()
call = Call()
concat = Join()
emph = Emph()
field = Field()
idem = Idempotent()
ifelse = IfElse()
inline = InLine()
join = Join()
link = Link()
url = Link()
optional = Optional()
ref = Reference()
sentence = Sentence()
text = Text()
words = Words()
