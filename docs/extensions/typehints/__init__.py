"""
    Autodoc typehints.

    Adapted from https://github.com/agronholm/sphinx-autodoc-typehints
"""
import inspect
import re
import typing
from typing import get_type_hints, TypeVar, Any, AnyStr, Generic, Union

from sphinx.util.inspect import Signature

try:
    from inspect import unwrap  # pylint: disable=C0412
except ImportError:
    def unwrap(func, *, stop=None):
        """This is the inspect.unwrap() method copied from Python 3.5's standard library."""
        if stop is None:
            def _is_wrapper(f):
                return hasattr(f, '__wrapped__')
        else:
            def _is_wrapper(f):
                return hasattr(f, '__wrapped__') and not stop(f)
        f = func  # remember the original func for error reporting
        memo = {id(f)}  # Memoise by id to tolerate non-hashable objects
        while _is_wrapper(func):
            func = func.__wrapped__
            id_func = id(func)
            if id_func in memo:
                raise ValueError('wrapper loop when unwrapping {!r}'.format(f))
            memo.add(id_func)
        return func


def format_cls(cls):
    """Formant a class."""
    return ':obj:`{}`'.format(cls)

def strip_role(text):
    """Strip role markup."""
    return re.sub(r'^:[A-z-:]+`([^`]+)`', r'\1', text)

class Formatter:
    """Class for formatting annotations."""

    def __call__(self, annotation):
        return self.format_annotation(annotation)

    def format_annotation(self, annotation):
        """Format an annotation."""
        if inspect.isclass(annotation) and annotation.__module__ == 'builtins':
            return self.format_builtin(annotation)

        try:
            klass = str(annotation.__origin__).split('.')[-1].lower()
        except AttributeError:
            try:
                klass = annotation.__name__
            except AttributeError:
                klass = annotation

        format_method = 'format_{}'.format(klass).lower()

        if hasattr(self, format_method):
            return getattr(self, format_method)(annotation)

        return str(klass)

    def format_builtin(self, annotation):  # pylint: disable=no-self-use
        """Format builtin types."""
        if annotation.__qualname__ == 'NoneType':
            return '``None``'
        return ':py:class:`{}`'.format(annotation.__qualname__)

    def format_union(self, annotation):
        """Format Union type."""
        params = annotation.__args__
        if params[-1].__qualname__ == 'NoneType':
            params = params[:-1]
        return ' | '.join(self.format_annotation(param)
                          for param in params)

    def format_list(self, annotation):
        """Format List type."""
        params = annotation.__args__
        return ':py:class:`list` of {}'.format(self(params[0]))

    def format_callable(self, annotation):
        """Format callable type."""
        params = annotation.__args__
        args = ', '.join(strip_role(self.format_annotation(param))
                         for param in params[:-1])
        return_type = strip_role(self.format_annotation(params[-1]))
        return ':py:class:`callable({}): {}`'.format(args, return_type)

    def format_dataframe(self, _):  # pylint: disable=no-self-use
        """Format dataframe."""
        return ':py:class:`pandas.DataFrame`'

    def format_ndarray(self, _):  # pylint: disable=no-self-use
        """Format ndarray."""
        return ':py:class:`numpy.ndarray`'

def format_annotation(annotation):
    """Format an annotation"""
    if inspect.isclass(annotation) and annotation.__module__ == 'builtins':
        if annotation.__qualname__ == 'NoneType':
            return '``None``'
        return ':py:class:`{}`'.format(annotation.__qualname__)

    return str(annotation.__class__.__name__)

def foo(annotation):
    annotation_cls = annotation if inspect.isclass(annotation) else type(annotation)
    class_name = None
    if annotation_cls.__module__ == 'typing':
        params = None
        prefix = ':py:class:'
        module = 'typing'
        extra = ''

        if inspect.isclass(getattr(annotation, '__origin__', None)):
            annotation_cls = annotation.__origin__
            try:
                if Generic in annotation_cls.mro():
                    module = annotation_cls.__module__
            except TypeError:
                pass  # annotation_cls was either the "type" object or typing.Type

        if annotation is Any:
            return ':py:data:`~typing.Any`'
        elif annotation is AnyStr:
            return ':py:data:`~typing.AnyStr`'
        elif isinstance(annotation, TypeVar):
            return '\\%r' % annotation
        elif (annotation is Union or getattr(annotation, '__origin__', None) is Union or
              hasattr(annotation, '__union_params__')):
            prefix = ':py:data:'
            class_name = 'Union'
            print(annotation.__args__)
            if hasattr(annotation, '__union_params__'):
                params = annotation.__union_params__
            elif hasattr(annotation, '__args__'):
                params = annotation.__args__

            if params and len(params) == 2 and (hasattr(params[1], '__qualname__') and
                                                params[1].__qualname__ == 'NoneType'):
                class_name = 'Optional'
                params = (params[0],)
        elif annotation_cls.__qualname__ == 'Tuple' and hasattr(annotation, '__tuple_params__'):
            params = annotation.__tuple_params__
            if annotation.__tuple_use_ellipsis__:
                params += (Ellipsis,)
        elif annotation_cls.__qualname__ == 'Callable':
            prefix = ':py:data:'
            arg_annotations = result_annotation = None
            if hasattr(annotation, '__result__'):
                arg_annotations = annotation.__args__
                result_annotation = annotation.__result__
            elif getattr(annotation, '__args__', None):
                arg_annotations = annotation.__args__[:-1]
                result_annotation = annotation.__args__[-1]

            if arg_annotations in (Ellipsis, (Ellipsis,)):
                params = [Ellipsis, result_annotation]
            elif arg_annotations is not None:
                params = [
                    '\\[{}]'.format(
                        ', '.join(format_annotation(param) for param in arg_annotations)),
                    result_annotation
                ]
        elif hasattr(annotation, 'type_var'):
            # Type alias
            class_name = annotation.name
            params = (annotation.type_var,)
        elif getattr(annotation, '__args__', None) is not None:
            params = annotation.__args__
        elif hasattr(annotation, '__parameters__'):
            params = annotation.__parameters__

        if params:
            #extra = '\\[{}]'.format(', '.join(format_annotation(param) for param in params))
            extra = '\\[{}]'.format(' | '.join(format_cls(param.__name__) for param in params))
        if not class_name:
            class_name = annotation_cls.__qualname__.title()

        return '{}`~{}.{}`{}'.format(prefix, module, class_name, extra)
    elif annotation is Ellipsis:
        return '...'
    elif inspect.isclass(annotation) or inspect.isclass(getattr(annotation, '__origin__', None)):
        if not inspect.isclass(annotation):
            annotation_cls = annotation.__origin__

        extra = ''
        if Generic in annotation_cls.mro():
            params = (getattr(annotation, '__parameters__', None) or
                      getattr(annotation, '__args__', None))
            extra = '\\[{}]'.format(', '.join(format_annotation(param) for param in params))

        return ':py:class:`~{}.{}`{}'.format(annotation.__module__, annotation_cls.__qualname__,
                                             extra)

    return str(annotation)

def format_list_annotation(annotation):
    """Format the list annotation."""



def process_signature(app, what: str, name: str, obj, options, signature, return_annotation):
    if not callable(obj):
        return

    if what in ('class', 'exception'):
        obj = getattr(obj, '__init__', getattr(obj, '__new__', None))

    if not getattr(obj, '__annotations__', None):
        return

    obj = unwrap(obj)
    signature = Signature(obj)
    parameters = [
        param.replace(annotation=inspect.Parameter.empty)
        for param in signature.signature.parameters.values()
    ]

    if parameters:
        if what in ('class', 'exception'):
            del parameters[0]
        elif what == 'method':
            outer = inspect.getmodule(obj)
            for clsname in obj.__qualname__.split('.')[:-1]:
                outer = getattr(outer, clsname)

            method_name = obj.__name__
            if method_name.startswith("__") and not method_name.endswith("__"):
                # If the method starts with double underscore (dunder)
                # Python applies mangling so we need to prepend the class name.
                # This doesn't happen if it always ends with double underscore.
                class_name = obj.__qualname__.split('.')[-2]
                method_name = "_{c}{m}".format(c=class_name, m=method_name)

            method_object = outer.__dict__[method_name]
            if not isinstance(method_object, (classmethod, staticmethod)):
                del parameters[0]

    signature.signature = signature.signature.replace(
        parameters=parameters,
        return_annotation=inspect.Signature.empty)

    return signature.format_args().replace('\\', '\\\\'), None


def process_docstring(app, what, name, obj, options, lines):
    if isinstance(obj, property):
        obj = obj.fget

    formatter = Formatter()
    if callable(obj):
        if what in ('class', 'exception'):
            obj = getattr(obj, '__init__')

        obj = unwrap(obj)
        try:
            type_hints = get_type_hints(obj)
        except (AttributeError, TypeError):
            # Introspecting a slot wrapper will raise TypeError
            return

        for argname, annotation in type_hints.items():
            if argname.endswith('_'):
                argname = '{}\\_'.format(argname[:-1])

            formatted_annotation = formatter(annotation)

            if argname == 'return':
                if what in ('class', 'exception'):
                    # Don't add return type None from __init__()
                    continue

                insert_index = len(lines)
                for i, line in enumerate(lines):
                    if line.startswith(':rtype:'):
                        insert_index = None
                        break
                    elif line.startswith(':return:') or line.startswith(':returns:'):
                        insert_index = i

                if insert_index is not None:
                    if insert_index == len(lines):
                        # Ensure that :rtype: doesn't get joined with a paragraph of text, which
                        # prevents it being interpreted.
                        lines.append('')
                        insert_index += 1

                    lines.insert(insert_index, ':rtype: {}'.format(formatted_annotation))
            else:
                searchfor = ':param {}:'.format(argname)
                for i, line in enumerate(lines):
                    if line.startswith(searchfor):
                        lines.insert(i, ':type {}: {}'.format(argname, formatted_annotation))
                        break


def config_ready(app, config):
    if config.set_type_checking_flag:
        typing.TYPE_CHECKING = True


def setup(app):
    app.add_config_value('set_type_checking_flag', True, 'html')
    app.connect('config-inited', config_ready)
    app.connect('autodoc-process-signature', process_signature)
    app.connect('autodoc-process-docstring', process_docstring)
    return dict(parallel_read_safe=True)