"""
Wellington Extension
"""
# pylint: disable=protected-access
from functools import partial

from sphinx.ext.napoleon import Config, _skip_member
from sphinx.ext.napoleon.docstring import NumpyDocstring


def _(message, *_):
    """
    NOOP implementation of sphinx.locale.get_translation shortcut.
    """
    return message


class VlnmDocstring(NumpyDocstring):

    def __init__(self, docstring, config=None, app=None, what='', name='',
                 obj=None, options=None):
        self._directive_sections = ['.. index::']
        self._sections = {
            'args': self._parse_parameters_section,
            'arguments': self._parse_parameters_section,
            'attention': partial(self._parse_admonition, 'attention'),
            'attributes': self._parse_attributes_section,
            'caution': partial(self._parse_admonition, 'caution'),
            'danger': partial(self._parse_admonition, 'danger'),
            'dataset': self._parse_dataset_section,
            'error': partial(self._parse_admonition, 'error'),
            'example': self._parse_examples_section,
            'examples': self._parse_examples_section,
            'hint': partial(self._parse_admonition, 'hint'),
            'important': partial(self._parse_admonition, 'important'),
            'keyword args': self._parse_keyword_arguments_section,
            'keyword arguments': self._parse_keyword_arguments_section,
            'methods': self._parse_methods_section,
            'note': partial(self._parse_admonition, 'note'),
            'notes': self._parse_notes_section,
            'other parameters': self._parse_other_parameters_section,
            'parameters': self._parse_parameters_section,
            'return': self._parse_returns_section,
            'returns': self._parse_returns_section,
            'raises': self._parse_raises_section,
            'references': self._parse_references_section,
            'see also': self._parse_see_also_section,
            'tip': partial(self._parse_admonition, 'tip'),
            'todo': partial(self._parse_admonition, 'todo'),
            'warning': partial(self._parse_admonition, 'warning'),
            'warnings': partial(self._parse_admonition, 'warning'),
            'warns': self._parse_warns_section,
            'yield': self._parse_yields_section,
            'yields': self._parse_yields_section,
        }
        super(VlnmDocstring, self).__init__(docstring, config, app, what,
                                            name, obj, options)

    def _parse_dataset_section(self, _section):
        # type: (unicode) -> List[unicode]
        return self._format_fields(_('Dataset columns'), self._consume_fields())

    def _format_fields(self, field_type, fields):
        # type: (unicode, List[Tuple[unicode, unicode, List[unicode]]]) -> List[unicode]
        field_type = ':%s:' % field_type.strip()
        padding = ' ' * len(field_type)
        multi = True  # len(fields) > 1
        lines = []  # type: List[unicode]
        for _name, _type, _desc in fields:
            field = self._format_field(_name, _type, _desc)
            if multi:
                if lines:
                    lines.extend(self._format_block(padding + ' * ', field))
                else:
                    lines.extend(self._format_block(field_type + ' * ', field))
            else:
                lines.extend(self._format_block(field_type + ' ', field))
        if lines and lines[-1]:
            lines.append('')

        return lines

    def _format_field(self, _name, _type, _desc):
        # type: (unicode, unicode, List[unicode]) -> List[unicode]
        _desc = self._strip_empty(_desc)
        has_desc = any(_desc)
        separator = ''  # has_desc and ' -- ' or ''
        if _name:
            if _type:
                if '`' in _type:
                    field = '**%s** (%s)%s' % (_name, _type, separator)  # type: unicode
                else:
                    field = '**%s** (*%s*)%s' % (_name, _type, separator)
            else:
                field = '**%s**%s' % (_name, separator)
        elif _type:
            if '`' in _type:
                field = '%s%s' % (_type, separator)
            else:
                field = '*%s*%s' % (_type, separator)
        else:
            field = ''

        if has_desc:
            _desc = self._fix_field_desc(_desc)
            return [field] + [''] + _desc
        return [field]


def _process_docstring(app, what, name, obj, options, lines):
    # type: (Sphinx, unicode, unicode, Any, Any, List[unicode]) -> None
    """Process the docstring for a given python object.
    Called when autodoc has read and processed a docstring. `lines` is a list
    of docstring lines that `_process_docstring` modifies in place to change
    what Sphinx outputs.
    The following settings in conf.py control what styles of docstrings will
    be parsed:
    * ``napoleon_google_docstring`` -- parse Google style docstrings
    * ``napoleon_numpy_docstring`` -- parse NumPy style docstrings
    Parameters
    ----------
    app : sphinx.application.Sphinx
        Application object representing the Sphinx process.
    what : str
        A string specifying the type of the object to which the docstring
        belongs. Valid values: "module", "class", "exception", "function",
        "method", "attribute".
    name : str
        The fully qualified name of the object.
    obj : module, class, exception, function, method, or attribute
        The object to which the docstring belongs.
    options : sphinx.ext.autodoc.Options
        The options given to the directive: an object with attributes
        inherited_members, undoc_members, show_inheritance and noindex that
        are True if the flag option of same name was given to the auto
        directive.
    lines : list of str
        The lines of the docstring, see above.
        .. note:: `lines` is modified *in place*
    """
    result_lines = lines
    docstring = VlnmDocstring(result_lines, app.config, app, what, name,
                              obj, options)
    result_lines = docstring.lines()
    lines[:] = result_lines[:]


def _patch_python_domain():
    # type: () -> None
    try:
        from sphinx.domains.python import PyTypedField
    except ImportError:
        pass
    else:
        import sphinx.domains.python
        from sphinx.locale import _
        for doc_field in sphinx.domains.python.PyObject.doc_field_types:
            if doc_field.name == 'parameter':
                doc_field.names = ('param', 'parameter', 'arg', 'argument')
                break
        sphinx.domains.python.PyObject.doc_field_types.append(
            PyTypedField('keyword', label=_('Keyword Arguments'),
                         names=('keyword', 'kwarg', 'kwparam'),
                         typerolename='obj', typenames=('paramtype', 'kwtype'),
                         can_collapse=True))


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]

    _patch_python_domain()

    app.setup_extension('sphinx.ext.autodoc')
    app.connect('autodoc-process-docstring', _process_docstring)
    app.connect('autodoc-skip-member', _skip_member)

    for name, (default, rebuild) in Config._config_values.items():
        app.add_config_value(name, default, rebuild)
