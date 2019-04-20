"""
    sphinx.domains.python
    ~~~~~~~~~~~~~~~~~~~~~

    The Python domain.

    :copyright: Copyright 2007-2019 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
import warnings
from typing import cast

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.deprecation import RemovedInSphinx40Warning
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index, IndexEntry
from sphinx.locale import _, __
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import make_refnode

if False:
    # For type annotation
    from typing import Any, Dict, Iterable, Iterator, List, Tuple, Type  # NOQA
    from sphinx.application import Sphinx  # NOQA
    from sphinx.builders import Builder  # NOQA
    from sphinx.environment import BuildEnvironment  # NOQA
    from sphinx.util.typing import TextlikeNode  # NOQA

logger = logging.getLogger(__name__)


# REs for Python signatures
py_sig_re = re.compile(
    r'''^ ([\w.]*\.)?            # class name(s)
          (\w+)  \s*             # thing name
          (?: \(\s*(.*)\s*\)     # optional: arguments
           (?:\s* -> \s* (.*))?  #           return annotation
          )? $                   # and nothing more
          ''', re.VERBOSE)


pairindextypes = {
    'module':    _('module'),
    'keyword':   _('keyword'),
    'operator':  _('operator'),
    'object':    _('object'),
    'exception': _('exception'),
    'statement': _('statement'),
    'builtin':   _('built-in function'),
}


def _pseudo_parse_arglist(signode, arglist):
    # type: (addnodes.desc_signature, str) -> None
    """"Parse" a list of arguments separated by commas.

    Arguments can have "optional" annotations given by enclosing them in
    brackets.  Currently, this will split at any comma, even if it's inside a
    string literal (e.g. default argument value).
    """
    paramlist = addnodes.desc_parameterlist()
    stack = [paramlist]  # type: List[nodes.Element]
    try:
        for argument in arglist.split(','):
            argument = argument.strip()
            ends_open = ends_close = 0
            while argument.startswith('['):
                stack.append(addnodes.desc_optional())
                stack[-2] += stack[-1]
                argument = argument[1:].strip()
            while argument.startswith(']'):
                stack.pop()
                argument = argument[1:].strip()
            while argument.endswith(']') and not argument.endswith('[]'):
                ends_close += 1
                argument = argument[:-1].strip()
            while argument.endswith('['):
                ends_open += 1
                argument = argument[:-1].strip()
            if argument:
                stack[-1] += addnodes.desc_parameter(argument, argument)
            while ends_open:
                stack.append(addnodes.desc_optional())
                stack[-2] += stack[-1]
                ends_open -= 1
            while ends_close:
                stack.pop()
                ends_close -= 1
        if len(stack) != 1:
            raise IndexError
    except IndexError:
        # if there are too few or too many elements on the stack, just give up
        # and treat the whole argument list as one argument, discarding the
        # already partially populated paramlist node
        paramlist = addnodes.desc_parameterlist()
        paramlist += addnodes.desc_parameter(arglist, arglist)
        signode += paramlist
    else:
        signode += paramlist


# This override allows our inline type specifiers to behave like :class: link
# when it comes to handling "." and "~" prefixes.
class PyXrefMixin:
    def make_xref(self,
                  rolename,                  # type: str
                  domain,                    # type: str
                  target,                    # type: str
                  innernode=nodes.emphasis,  # type: Type[TextlikeNode]
                  contnode=None,             # type: nodes.Node
                  env=None,                  # type: BuildEnvironment
                  ):
        # type: (...) -> nodes.Node
        result = super().make_xref(rolename, domain, target,  # type: ignore
                                   innernode, contnode, env)
        result['refspecific'] = True
        if target.startswith(('.', '~')):
            prefix, result['reftarget'] = target[0], target[1:]
            if prefix == '.':
                text = target[1:]
            elif prefix == '~':
                text = target.split('.')[-1]
            for node in result.traverse(nodes.Text):
                node.parent[node.parent.index(node)] = nodes.Text(text)
                break
        return result

    def make_xrefs(self,
                   rolename,                  # type: str
                   domain,                    # type: str
                   target,                    # type: str
                   innernode=nodes.emphasis,  # type: Type[TextlikeNode]
                   contnode=None,             # type: nodes.Node
                   env=None,                  # type: BuildEnvironment
                   ):
        # type: (...) -> List[nodes.Node]
        delims = r'(\s*[\[\]\(\),](?:\s*or\s)?\s*|\s+or\s+)'
        delims_re = re.compile(delims)
        sub_targets = re.split(delims, target)

        split_contnode = bool(contnode and contnode.astext() == target)

        results = []
        for sub_target in filter(None, sub_targets):
            if split_contnode:
                contnode = nodes.Text(sub_target)

            if delims_re.match(sub_target):
                results.append(contnode or innernode(sub_target, sub_target))
            else:
                results.append(self.make_xref(rolename, domain, sub_target,
                                              innernode, contnode, env))

        return results


class PyField(PyXrefMixin, Field):
    def make_xref(self, rolename, domain, target,
                  innernode=nodes.emphasis, contnode=None, env=None):
        # type: (str, str, str, Type[TextlikeNode], nodes.Node, BuildEnvironment) ->  nodes.Node  # NOQA
        if rolename == 'class' and target == 'None':
            # None is not a type, so use obj role instead.
            rolename = 'obj'

        return super().make_xref(rolename, domain, target, innernode, contnode, env)


class PyGroupedField(PyXrefMixin, GroupedField):
    pass


class PyTypedField(PyXrefMixin, Field):
    """
    A doc field that is grouped and has type information for the arguments.  It
    always has an argument.  The argument can be linked using the given
    *rolename*, the type using the given *typerolename*.
    Two uses are possible: either parameter and type description are given
    separately, using a field from *names* and one from *typenames*,
    respectively, or both are given using a field from *names*, see the example.
    Example::
       :param foo: description of parameter foo
       :type foo:  SomeClass
       -- or --
       :param SomeClass foo: description of parameter foo
    """
    is_typed = True

    def __init__(self, name, names=(), typenames=(), label=None,
                 rolename=None, typerolename=None, can_collapse=False):
        print(name, names, typenames)
        # type: (str, Tuple[str, ...], Tuple[str, ...], str, str, str, bool) -> None
        super().__init__(name, names, label, rolename, can_collapse)
        self.typenames = typenames
        self.typerolename = typerolename

    def make_entry(self, fieldarg, content):
        print(fieldarg, content)
        # type: (str, List[nodes.Node]) -> Tuple[str, List[nodes.Node]]
        return (fieldarg, content)

    def make_field(self,
                   types,     # type: Dict[str, List[nodes.Node]]
                   domain,    # type: str
                   items,     # type: Tuple
                   env=None,  # type: BuildEnvironment
                   ):
        print(types, domain, item)
        # type: (...) -> nodes.field
        def handle_item(fieldarg, content):
            # type: (str, str) -> nodes.paragraph
            par = nodes.paragraph()
            par.extend(self.make_xrefs(self.rolename, domain, fieldarg,
                                       addnodes.literal_strong, env=env))
            if fieldarg in types:
                par += nodes.Text(' (')
                # NOTE: using .pop() here to prevent a single type node to be
                # inserted twice into the doctree, which leads to
                # inconsistencies later when references are resolved
                fieldtype = types.pop(fieldarg)
                if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                    typename = fieldtype[0].astext()
                    par.extend(self.make_xrefs(self.typerolename, domain, typename,
                                               addnodes.literal_emphasis, env=env))
                else:
                    par += fieldtype
                par += nodes.Text(')')
            par += nodes.Text(' -- ')
            par += content
            return par

        fieldname = nodes.field_name('', self.label)
        if len(items) == 1 and self.can_collapse:
            fieldarg, content = items[0]
            bodynode = handle_item(fieldarg, content)  # type: nodes.Node
        else:
            bodynode = self.list_type()
            for fieldarg, content in items:
                bodynode += nodes.list_item('', handle_item(fieldarg, content))
        fieldbody = nodes.field_body('', bodynode)

        return nodes.field('', fieldname, fieldbody)

    def make_xref(self, rolename, domain, target,
                  innernode=nodes.emphasis, contnode=None, env=None):
        # type: (str, str, str, Type[TextlikeNode], nodes.Node, BuildEnvironment) ->  nodes.Node  # NOQA
        if rolename == 'class' and target == 'None':
            # None is not a type, so use obj role instead.
            rolename = 'obj'

        return super().make_xref(rolename, domain, target, innernode, contnode, env)


class PyObject(ObjectDescription):
    """
    Description of a general Python object.

    :cvar allow_nesting: Class is an object that allows for nested namespaces
    :vartype allow_nesting: bool
    """
    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
        'annotation': directives.unchanged,
    }

    doc_field_types = [
        PyTypedField('parameter', label=_('Parameters'),
                     names=('param', 'parameter', 'arg', 'argument',
                            'keyword', 'kwarg', 'kwparam'),
                     typerolename='class', typenames=('paramtype', 'type'),
                     can_collapse=True),
        PyTypedField('variable', label=_('Variables'), rolename='obj',
                     names=('var', 'ivar', 'cvar'),
                     typerolename='class', typenames=('vartype',),
                     can_collapse=True),
        PyGroupedField('exceptions', label=_('Raises'), rolename='exc',
                       names=('raises', 'raise', 'exception', 'except'),
                       can_collapse=True),
        Field('returnvalue', label=_('Returns'), has_arg=False,
              names=('returns', 'return')),
        PyField('returntype', label=_('Return type'), has_arg=False,
                names=('rtype',), bodyrolename='class'),
    ]

    allow_nesting = False

    def get_signature_prefix(self, sig):
        # type: (str) -> str
        """May return a prefix to put before the object name in the
        signature.
        """
        return ''

    def needs_arglist(self):
        # type: () -> bool
        """May return true if an empty argument list is to be generated even if
        the document contains none.
        """
        return False

    def handle_signature(self, sig, signode):
        # type: (str, addnodes.desc_signature) -> Tuple[str, str]
        """Transform a Python signature into RST nodes.

        Return (fully qualified name of the thing, classname if any).

        If inside a class, the current class name is handled intelligently:
        * it is stripped from the displayed name if present
        * it is added to the full name (return value) if not present
        """
        m = py_sig_re.match(sig)
        if m is None:
            raise ValueError
        prefix, name, arglist, retann = m.groups()

        # determine module and class name (if applicable), as well as full name
        modname = self.options.get('module', self.env.ref_context.get('pyv:module'))
        classname = self.env.ref_context.get('pyv:class')
        if classname:
            add_module = False
            if prefix and (prefix == classname or
                           prefix.startswith(classname + ".")):
                fullname = prefix + name
                # class name is given again in the signature
                prefix = prefix[len(classname):].lstrip('.')
            elif prefix:
                # class name is given in the signature, but different
                # (shouldn't happen)
                fullname = classname + '.' + prefix + name
            else:
                # class name is not given in the signature
                fullname = classname + '.' + name
        else:
            add_module = True
            if prefix:
                classname = prefix.rstrip('.')
                fullname = prefix + name
            else:
                classname = ''
                fullname = name

        signode['module'] = modname
        signode['class'] = classname
        signode['fullname'] = fullname

        sig_prefix = self.get_signature_prefix(sig)
        if sig_prefix:
            signode += addnodes.desc_annotation(sig_prefix, sig_prefix)

        if prefix:
            signode += addnodes.desc_addname(prefix, prefix)
        elif add_module and self.env.config.add_module_names:
            if modname and modname != 'exceptions':
                # exceptions are a special case, since they are documented in the
                # 'exceptions' module.
                nodetext = modname + '.'
                signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(name, name)
        if arglist:
            _pseudo_parse_arglist(signode, arglist)
        else:
            if self.needs_arglist():
                # for callables, add an empty parameter list
                signode += addnodes.desc_parameterlist()

        if retann:
            signode += addnodes.desc_returns(retann, retann)

        anno = self.options.get('annotation')
        if anno:
            signode += addnodes.desc_annotation(' ' + anno, ' ' + anno)

        return fullname, prefix

    def get_index_text(self, modname, name):
        # type: (str, Tuple[str, str]) -> str
        """Return the text for the index entry of the object."""
        raise NotImplementedError('must be implemented in subclasses')

    def add_target_and_index(self, name_cls, sig, signode):
        # type: (Tuple[str, str], str, addnodes.desc_signature) -> None
        modname = self.options.get('module', self.env.ref_context.get('pyv:module'))
        fullname = (modname and modname + '.' or '') + name_cls[0]
        # note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)

            domain = cast(PythonDomain, self.env.get_domain('pyv'))
            domain.note_object(fullname, self.objtype)

        indextext = self.get_index_text(modname, name_cls)
        if indextext:
            self.indexnode['entries'].append(('single', indextext,
                                              fullname, '', None))

    def before_content(self):
        # type: () -> None
        """Handle object nesting before content

        :pyv:class:`PyObject` represents Python language constructs. For
        constructs that are nestable, such as a Python classes, this method will
        build up a stack of the nesting heirarchy so that it can be later
        de-nested correctly, in :pyv:meth:`after_content`.

        For constructs that aren't nestable, the stack is bypassed, and instead
        only the most recent object is tracked. This object prefix name will be
        removed with :pyv:meth:`after_content`.
        """
        prefix = None
        if self.names:
            # fullname and name_prefix come from the `handle_signature` method.
            # fullname represents the full object name that is constructed using
            # object nesting and explicit prefixes. `name_prefix` is the
            # explicit prefix given in a signature
            (fullname, name_prefix) = self.names[-1]
            if self.allow_nesting:
                prefix = fullname
            elif name_prefix:
                prefix = name_prefix.strip('.')
        if prefix:
            self.env.ref_context['pyv:class'] = prefix
            if self.allow_nesting:
                classes = self.env.ref_context.setdefault('pyv:classes', [])
                classes.append(prefix)
        if 'module' in self.options:
            modules = self.env.ref_context.setdefault('pyv:modules', [])
            modules.append(self.env.ref_context.get('pyv:module'))
            self.env.ref_context['pyv:module'] = self.options['module']

    def after_content(self):
        # type: () -> None
        """Handle object de-nesting after content

        If this class is a nestable object, removing the last nested class prefix
        ends further nesting in the object.

        If this class is not a nestable object, the list of classes should not
        be altered as we didn't affect the nesting levels in
        :pyv:meth:`before_content`.
        """
        classes = self.env.ref_context.setdefault('pyv:classes', [])
        if self.allow_nesting:
            try:
                classes.pop()
            except IndexError:
                pass
        self.env.ref_context['pyv:class'] = (classes[-1] if len(classes) > 0
                                            else None)
        if 'module' in self.options:
            modules = self.env.ref_context.setdefault('pyv:modules', [])
            if modules:
                self.env.ref_context['pyv:module'] = modules.pop()
            else:
                self.env.ref_context.pop('pyv:module')


class PyModulelevel(PyObject):
    """
    Description of an object on module level (functions, data).
    """

    def run(self):
        # type: () -> List[nodes.Node]
        warnings.warn('PyClassmember is deprecated.',
                      RemovedInSphinx40Warning)

        return super().run()

    def needs_arglist(self):
        # type: () -> bool
        return self.objtype == 'function'

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        if self.objtype == 'function':
            if not modname:
                return _('%s() (built-in function)') % name_cls[0]
            return _('%s() (in module %s)') % (name_cls[0], modname)
        elif self.objtype == 'data':
            if not modname:
                return _('%s (built-in variable)') % name_cls[0]
            return _('%s (in module %s)') % (name_cls[0], modname)
        else:
            return ''


class PyFunction(PyObject):
    """Description of a function."""

    def needs_arglist(self):
        # type: () -> bool
        return True

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        if modname:
            return _('%s() (in module %s)') % (name, modname)
        else:
            return _('%s() (built-in function)') % name


class PyVariable(PyObject):
    """Description of a variable."""

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        if modname:
            return _('%s (in module %s)') % (name, modname)
        else:
            return _('%s (built-in variable)') % name


class PyClasslike(PyObject):
    """
    Description of a class-like object (classes, interfaces, exceptions).
    """

    allow_nesting = True

    def get_signature_prefix(self, sig):
        # type: (str) -> str
        return self.objtype + ' '

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        if self.objtype == 'class':
            if not modname:
                return _('%s (built-in class)') % name_cls[0]
            return _('%s (class in %s)') % (name_cls[0], modname)
        elif self.objtype == 'exception':
            return name_cls[0]
        else:
            return ''


class PyClassmember(PyObject):
    """
    Description of a class member (methods, attributes).
    """

    def run(self):
        # type: () -> List[nodes.Node]
        warnings.warn('PyClassmember is deprecated.',
                      RemovedInSphinx40Warning)

        return super().run()

    def needs_arglist(self):
        # type: () -> bool
        return self.objtype.endswith('method')

    def get_signature_prefix(self, sig):
        # type: (str) -> str
        if self.objtype == 'staticmethod':
            return 'static '
        elif self.objtype == 'classmethod':
            return 'classmethod '
        return ''

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        add_modules = self.env.config.add_module_names
        if self.objtype == 'method':
            try:
                clsname, methname = name.rsplit('.', 1)
            except ValueError:
                if modname:
                    return _('%s() (in module %s)') % (name, modname)
                else:
                    return '%s()' % name
            if modname and add_modules:
                return _('%s() (%s.%s method)') % (methname, modname, clsname)
            else:
                return _('%s() (%s method)') % (methname, clsname)
        elif self.objtype == 'staticmethod':
            try:
                clsname, methname = name.rsplit('.', 1)
            except ValueError:
                if modname:
                    return _('%s() (in module %s)') % (name, modname)
                else:
                    return '%s()' % name
            if modname and add_modules:
                return _('%s() (%s.%s static method)') % (methname, modname,
                                                          clsname)
            else:
                return _('%s() (%s static method)') % (methname, clsname)
        elif self.objtype == 'classmethod':
            try:
                clsname, methname = name.rsplit('.', 1)
            except ValueError:
                if modname:
                    return _('%s() (in module %s)') % (name, modname)
                else:
                    return '%s()' % name
            if modname:
                return _('%s() (%s.%s class method)') % (methname, modname,
                                                         clsname)
            else:
                return _('%s() (%s class method)') % (methname, clsname)
        elif self.objtype == 'attribute':
            try:
                clsname, attrname = name.rsplit('.', 1)
            except ValueError:
                if modname:
                    return _('%s (in module %s)') % (name, modname)
                else:
                    return name
            if modname and add_modules:
                return _('%s (%s.%s attribute)') % (attrname, modname, clsname)
            else:
                return _('%s (%s attribute)') % (attrname, clsname)
        else:
            return ''


class PyMethod(PyObject):
    """Description of a method."""

    def needs_arglist(self):
        # type: () -> bool
        return True

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        try:
            clsname, methname = name.rsplit('.', 1)
            if modname and self.env.config.add_module_names:
                clsname = '.'.join([modname, clsname])
        except ValueError:
            if modname:
                return _('%s() (in module %s)') % (name, modname)
            else:
                return '%s()' % name

        return _('%s() (%s method)') % (methname, clsname)


class PyClassMethod(PyMethod):
    """Description of a classmethod."""

    def get_signature_prefix(self, sig):
        # type: (str) -> str
        return 'classmethod '

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        try:
            clsname, methname = name.rsplit('.', 1)
            if modname and self.env.config.add_module_names:
                clsname = '.'.join([modname, clsname])
        except ValueError:
            if modname:
                return _('%s() (in module %s)') % (name, modname)
            else:
                return '%s()' % name

        return _('%s() (%s class method)') % (methname, clsname)


class PyStaticMethod(PyMethod):
    """Description of a staticmethod."""

    def get_signature_prefix(self, sig):
        # type: (str) -> str
        return 'static '

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        try:
            clsname, methname = name.rsplit('.', 1)
            if modname and self.env.config.add_module_names:
                clsname = '.'.join([modname, clsname])
        except ValueError:
            if modname:
                return _('%s() (in module %s)') % (name, modname)
            else:
                return '%s()' % name

        return _('%s() (%s static method)') % (methname, clsname)


class PyAttribute(PyObject):
    """Description of an attribute."""

    def get_index_text(self, modname, name_cls):
        # type: (str, Tuple[str, str]) -> str
        name, cls = name_cls
        try:
            clsname, attrname = name.rsplit('.', 1)
            if modname and self.env.config.add_module_names:
                clsname = '.'.join([modname, clsname])
        except ValueError:
            if modname:
                return _('%s (in module %s)') % (name, modname)
            else:
                return name

        return _('%s (%s attribute)') % (attrname, clsname)


class PyDecoratorMixin:
    """
    Mixin for decorator directives.
    """
    def handle_signature(self, sig, signode):
        # type: (str, addnodes.desc_signature) -> Tuple[str, str]
        ret = super().handle_signature(sig, signode)  # type: ignore
        signode.insert(0, addnodes.desc_addname('@', '@'))
        return ret

    def needs_arglist(self):
        # type: () -> bool
        return False


class PyDecoratorFunction(PyDecoratorMixin, PyModulelevel):
    """
    Directive to mark functions meant to be used as decorators.
    """
    def run(self):
        # type: () -> List[nodes.Node]
        # a decorator function is a function after all
        self.name = 'pyv:function'
        return super().run()


class PyDecoratorMethod(PyDecoratorMixin, PyClassmember):
    """
    Directive to mark methods meant to be used as decorators.
    """
    def run(self):
        # type: () -> List[nodes.Node]
        self.name = 'pyv:method'
        return super().run()


class PyModule(SphinxDirective):
    """
    Directive to mark description of a new module.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        # type: () -> List[nodes.Node]
        domain = cast(PythonDomain, self.env.get_domain('pyv'))

        modname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        self.env.ref_context['pyv:module'] = modname
        ret = []  # type: List[nodes.Node]
        if not noindex:
            # note module to the domain
            domain.note_module(modname,
                               self.options.get('synopsis', ''),
                               self.options.get('platform', ''),
                               'deprecated' in self.options)
            domain.note_object(modname, 'module')

            targetnode = nodes.target('', '', ids=['module-' + modname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (module)') % modname
            inode = addnodes.index(entries=[('single', indextext,
                                             'module-' + modname, '', None)])
            ret.append(inode)
        return ret


class PyCurrentModule(SphinxDirective):
    """
    This directive is just to tell Sphinx that we're documenting
    stuff in module foo, but links to module foo won't lead here.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}  # type: Dict

    def run(self):
        # type: () -> List[nodes.Node]
        modname = self.arguments[0].strip()
        if modname == 'None':
            self.env.ref_context.pop('pyv:module', None)
        else:
            self.env.ref_context['pyv:module'] = modname
        return []


class PyXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        # type: (BuildEnvironment, nodes.Element, bool, str, str) -> Tuple[str, str]
        refnode['pyv:module'] = env.ref_context.get('pyv:module')
        refnode['pyv:class'] = env.ref_context.get('pyv:class')
        if not has_explicit_title:
            title = title.lstrip('.')    # only has a meaning for the target
            target = target.lstrip('~')  # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot + 1:]
        # if the first character is a dot, search more specific namespaces first
        # else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class PythonModuleIndex(Index):
    """
    Index subclass to provide the Python module index.
    """

    name = 'modindex'
    localname = _('Python Module Index')
    shortname = _('modules')

    def generate(self, docnames=None):
        # type: (Iterable[str]) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]
        content = {}  # type: Dict[str, List[IndexEntry]]
        # list of prefixes to ignore
        ignores = None  # type: List[str]
        ignores = self.domain.env.config['modindex_common_prefix']  # type: ignore
        ignores = sorted(ignores, key=len, reverse=True)
        # list of all modules, sorted by module name
        modules = sorted(self.domain.data['modules'].items(),
                         key=lambda x: x[0].lower())
        # sort out collapsable modules
        prev_modname = ''
        num_toplevels = 0
        for modname, (docname, synopsis, platforms, deprecated) in modules:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if modname.startswith(ignore):
                    modname = modname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''

            # we stripped the whole module name?
            if not modname:
                modname, stripped = stripped, ''

            entries = content.setdefault(modname[0].lower(), [])

            package = modname.split('.')[0]
            if package != modname:
                # it's a submodule
                if prev_modname == package:
                    # first submodule - make parent a group head
                    if entries:
                        last = entries[-1]
                        entries[-1] = IndexEntry(last[0], 1, last[2], last[3],
                                                 last[4], last[5], last[6])
                    entries.append(IndexEntry(stripped + package, 1, '', '', '', '', ''))
                elif not prev_modname.startswith(package):
                    # submodule without parent in list, add dummy entry
                    entries.append(IndexEntry(stripped + package, 1, '', '', '', '', ''))
                subtype = 2
            else:
                num_toplevels += 1
                subtype = 0

            qualifier = deprecated and _('Deprecated') or ''
            entries.append(IndexEntry(stripped + modname, subtype, docname,
                                      'module-' + stripped + modname, platforms,
                                      qualifier, synopsis))
            prev_modname = modname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel modules is larger than
        # number of submodules
        collapse = len(modules) - num_toplevels < num_toplevels

        # sort by first letter
        sorted_content = sorted(content.items())

        return sorted_content, collapse


class PythonDomain(Domain):
    """Python language domain."""
    name = 'pyv'
    label = 'Python'
    object_types = {
        'function':     ObjType(_('function'),      'func', 'obj'),
        'data':         ObjType(_('data'),          'data', 'obj'),
        'class':        ObjType(_('class'),         'class', 'exc', 'obj'),
        'exception':    ObjType(_('exception'),     'exc', 'class', 'obj'),
        'method':       ObjType(_('method'),        'meth', 'obj'),
        'classmethod':  ObjType(_('class method'),  'meth', 'obj'),
        'staticmethod': ObjType(_('static method'), 'meth', 'obj'),
        'attribute':    ObjType(_('attribute'),     'attr', 'obj'),
        'module':       ObjType(_('module'),        'mod', 'obj'),
    }  # type: Dict[str, ObjType]

    directives = {
        'function':        PyFunction,
        'data':            PyVariable,
        'class':           PyClasslike,
        'exception':       PyClasslike,
        'method':          PyMethod,
        'classmethod':     PyClassMethod,
        'staticmethod':    PyStaticMethod,
        'attribute':       PyAttribute,
        'module':          PyModule,
        'currentmodule':   PyCurrentModule,
        'decorator':       PyDecoratorFunction,
        'decoratormethod': PyDecoratorMethod,
    }
    roles = {
        'data':  PyXRefRole(),
        'exc':   PyXRefRole(),
        'func':  PyXRefRole(fix_parens=True),
        'class': PyXRefRole(),
        'const': PyXRefRole(),
        'attr':  PyXRefRole(),
        'meth':  PyXRefRole(fix_parens=True),
        'mod':   PyXRefRole(),
        'obj':   PyXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'modules': {},  # modname -> docname, synopsis, platform, deprecated
    }  # type: Dict[str, Dict[str, Tuple[Any]]]
    indices = [
        PythonModuleIndex,
    ]

    @property
    def objects(self):
        # type: () -> Dict[str, Tuple[str, str]]
        return self.data.setdefault('objects', {})  # fullname -> docname, objtype

    def note_object(self, name, objtype, location=None):
        # type: (str, str, Any) -> None
        """Note a python object for cross reference.

        .. versionadded:: 2.1
        """
        if name in self.objects:
            docname = self.objects[name][0]
            logger.warning(__('duplicate object description of %s, '
                              'other instance in %s, use :noindex: for one of them'),
                           name, docname, location=location)
        self.objects[name] = (self.env.docname, objtype)

    @property
    def modules(self):
        # type: () -> Dict[str, Tuple[str, str, str, bool]]
        return self.data.setdefault('modules', {})  # modname -> docname, synopsis, platform, deprecated  # NOQA

    def note_module(self, name, synopsis, platform, deprecated):
        # type: (str, str, str, bool) -> None
        """Note a python module for cross reference.

        .. versionadded:: 2.1
        """
        self.modules[name] = (self.env.docname, synopsis, platform, deprecated)

    def clear_doc(self, docname):
        # type: (str) -> None
        for fullname, (fn, _l) in list(self.objects.items()):
            if fn == docname:
                del self.objects[fullname]
        for modname, (fn, _x, _x, _y) in list(self.modules.items()):
            if fn == docname:
                del self.modules[modname]

    def merge_domaindata(self, docnames, otherdata):
        # type: (List[str], Dict) -> None
        # XXX check duplicates?
        for fullname, (fn, objtype) in otherdata['objects'].items():
            if fn in docnames:
                self.objects[fullname] = (fn, objtype)
        for modname, data in otherdata['modules'].items():
            if data[0] in docnames:
                self.modules[modname] = data

    def find_obj(self, env, modname, classname, name, type, searchmode=0):
        # type: (BuildEnvironment, str, str, str, str, int) -> List[Tuple[str, Any]]
        """Find a Python object for "name", perhaps using the given module
        and/or classname.  Returns a list of (name, object entry) tuples.
        """
        # skip parens
        if name[-2:] == '()':
            name = name[:-2]

        if not name:
            return []

        matches = []  # type: List[Tuple[str, Any]]

        newname = None
        if searchmode == 1:
            if type is None:
                objtypes = list(self.object_types)
            else:
                objtypes = self.objtypes_for_role(type)
            if objtypes is not None:
                if modname and classname:
                    fullname = modname + '.' + classname + '.' + name
                    if fullname in self.objects and self.objects[fullname][1] in objtypes:
                        newname = fullname
                if not newname:
                    if modname and modname + '.' + name in self.objects and \
                       self.objects[modname + '.' + name][1] in objtypes:
                        newname = modname + '.' + name
                    elif name in self.objects and self.objects[name][1] in objtypes:
                        newname = name
                    else:
                        # "fuzzy" searching mode
                        searchname = '.' + name
                        matches = [(oname, self.objects[oname]) for oname in self.objects
                                   if oname.endswith(searchname) and
                                   self.objects[oname][1] in objtypes]
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in self.objects:
                newname = name
            elif type == 'mod':
                # only exact matches allowed for modules
                return []
            elif classname and classname + '.' + name in self.objects:
                newname = classname + '.' + name
            elif modname and modname + '.' + name in self.objects:
                newname = modname + '.' + name
            elif modname and classname and \
                    modname + '.' + classname + '.' + name in self.objects:
                newname = modname + '.' + classname + '.' + name
            # special case: builtin exceptions have module "exceptions" set
            elif type == 'exc' and '.' not in name and \
                    'exceptions.' + name in self.objects:
                newname = 'exceptions.' + name
            # special case: object methods
            elif type in ('func', 'meth') and '.' not in name and \
                    'object.' + name in self.objects:
                newname = 'object.' + name
        if newname is not None:
            matches.append((newname, self.objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder,
                     type, target, node, contnode):
        # type: (BuildEnvironment, str, Builder, str, str, addnodes.pending_xref, nodes.Element) -> nodes.Element  # NOQA
        modname = node.get('pyv:module')
        clsname = node.get('pyv:class')
        searchmode = node.hasattr('refspecific') and 1 or 0
        matches = self.find_obj(env, modname, clsname, target,
                                type, searchmode)
        if not matches:
            return None
        elif len(matches) > 1:
            logger.warning(__('more than one target found for cross-reference %r: %s'),
                           target, ', '.join(match[0] for match in matches),
                           type='ref', subtype='python', location=node)
        name, obj = matches[0]

        if obj[1] == 'module':
            return self._make_module_refnode(builder, fromdocname, name, contnode)
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode, name)

    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        # type: (BuildEnvironment, str, Builder, str, addnodes.pending_xref, nodes.Element) -> List[Tuple[str, nodes.Element]]  # NOQA
        modname = node.get('pyv:module')
        clsname = node.get('pyv:class')
        results = []  # type: List[Tuple[str, nodes.Element]]

        # always search in "refspecific" mode with the :any: role
        matches = self.find_obj(env, modname, clsname, target, None, 1)
        for name, obj in matches:
            if obj[1] == 'module':
                results.append(('pyv:mod',
                                self._make_module_refnode(builder, fromdocname,
                                                          name, contnode)))
            else:
                results.append(('pyv:' + self.role_for_objtype(obj[1]),
                                make_refnode(builder, fromdocname, obj[0], name,
                                             contnode, name)))
        return results

    def _make_module_refnode(self, builder, fromdocname, name, contnode):
        # type: (Builder, str, str, nodes.Node) -> nodes.Element
        # get additional info for modules
        docname, synopsis, platform, deprecated = self.modules[name]
        title = name
        if synopsis:
            title += ': ' + synopsis
        if deprecated:
            title += _(' (deprecated)')
        if platform:
            title += ' (' + platform + ')'
        return make_refnode(builder, fromdocname, docname,
                            'module-' + name, contnode, title)

    def get_objects(self):
        # type: () -> Iterator[Tuple[str, str, str, str, str, int]]
        for modname, info in self.modules.items():
            yield (modname, modname, 'module', info[0], 'module-' + modname, 0)
        for refname, (docname, type) in self.objects.items():
            if type != 'module':  # modules are already handled
                yield (refname, refname, type, docname, refname, 1)

    def get_full_qualified_name(self, node):
        # type: (nodes.Element) -> str
        modname = node.get('pyv:module')
        clsname = node.get('pyv:class')
        target = node.get('reftarget')
        if target is None:
            return None
        else:
            return '.'.join(filter(None, [modname, clsname, target]))


def setup(app):
    # type: (Sphinx) -> Dict[str, Any]
    app.add_domain(PythonDomain)

    return {
        'version': 'builtin',
        'env_version': 1,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
