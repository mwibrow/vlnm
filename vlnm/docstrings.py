"""
Module for inserting common documentation snippits into docstrings.
"""
import re
import textwrap


REPLACEMENTS = {
    'f0:': r"""
        DataFrame columns containing :math:`F_0` data.
        If omitted, defaults to ``'f0'``.
    """,
    'f1:': r"""
        DataFrame columns containing :math:`F_1` data.
        If omitted, defaults to ``'f1'``.
    """,
    'f2:': r"""
        DataFrame columns containing :math:`F_2` data.
        If omitted, defaults to ``'f2'``.
    """,
    'f3:': r"""
        DataFrame columns containing :math:`F_2` data.
        If omitted, defaults to ``'f2'``.
    """,
    'f0, f1, f2, f3:': r"""
    f0, f1, f2, f3: :obj:`str` or :obj:`list` of :obj:`str`

        :class:`DataFrame` columns containing formant data.
        If omitted, any columns from the list
        ``['f0', 'f1', 'f2', 'f3']`` that
        are in the DataFrame will be used.
    """,
    'f0, f1, f2, f3, f4, f5:': r"""
    f0, f1, f2, f3, f4, f5: :obj:`str` or :obj:`list` of :obj:`str`

        :class:`DataFrame` columns containing formant data.
        If omitted, any columns from the list
        ``['f0', 'f1', 'f2', 'f3', 'f4', 'f5']`` that
        are in the DataFrame will be used.
    """,
    'formants:': r"""
        The :class:`DataFrame` columns containing the formant data.
        If omitted, any columns matching
        ``'f0'``, ``'f1'``, ``'f2'``, ``'f3'``, ``'f4'``, or ``'f5'``
        will be used.
    """,
    'rename:': r"""
        If specified as a :obj:`str`
        rename output columns according to the
        specified pattern replacing ``{}``
        with the output column.

        If specified as a :obj:`dict`,
        output columns will only be renamed if they have an entry
        in the dictionary, taking the value in
        the dictionary as the new column name.
        If the value is :obj:`None` the
        output column will be removed.
    """,
    'speaker:': r"""
        The DataFrame column which contains the speaker labels.
        If not given, defaults to ``'speaker'``.
    """,
    'vowel:': r"""
        The DataFrame column which contains the vowel labels.
        If not given, defaults to ``'vowel'``.
    """,
    ('kwargs:', 'type'): r"""
        Optional keyword arguments passed to the parent constructor.
    """,
    'groups:': r"""
        One or more Dataframe columns over which to group
        the data before applying the normalizer.
    """,
    'normalize': r"""
    Normalize formant data.

    Parameters
    ----------

    df:
        DataFrame containing formant data.

    **kwargs:
        Passed to the parent method.

    Returns
    -------
    :
        A dataframe containing the normalized formants.
    """
}

REPLACEMENTS = {
    'type.parameters': {
        'f0:': dict(
            description=r"""
            DataFrame columns containing :math:`F_0` data.
            If omitted, defaults to ``'f0'``."""),
        'f1:': dict(
            description=r"""
            DataFrame columns containing :math:`F_1` data.
            If omitted, defaults to ``'f1'``."""),
        'f2:': dict(
            description=r"""
            DataFrame columns containing :math:`F_2` data.
            If omitted, defaults to ``'f2'``."""),
        'f3:': dict(
            description=r"""
            DataFrame columns containing :math:`F_3` data.
            If omitted, defaults to ``'f3'``."""),
        'f1 - f2:': dict(
            parameter=r"""f1, f2: :obj:`str` or :obj:`list` of :obj:`str`""",
            description=r"""
            :class:`DataFrame` columns containing formant data.
            If omitted, any columns from the list
            ``['f1', 'f2']`` that
            are in the DataFrame will be used."""),
        'f0 - f3:': dict(
            parameter=r"""f0, f1, f2, f3: :obj:`str` or :obj:`list` of :obj:`str`""",
            description=r"""
            :class:`DataFrame` columns containing formant data.
            If omitted, any columns from the list
            ``['f0', 'f1', 'f2', 'f3']`` that
            are in the DataFrame will be used."""),
        'f0 - f5:': dict(
            parameter=r"""f0, f1, …. f5: :obj:`str` or :obj:`list` of :obj:`str`""",
            description=r"""
            :class:`DataFrame` columns containing formant data.
            If omitted, any columns from the list
            ``['f0', 'f1', 'f2', 'f3', 'f4', 'f5']`` that
            are in the DataFrame will be used."""),
        'kwargs:': dict(
            parameter=r"""\*\*kwargs:""",
            description=r"""
            Optional keyword arguments passed to the parent constructor.
        """),
        'speaker:': dict(
            description=r"""
            The DataFrame column which contains the speaker labels.
            If not given, defaults to ``'speaker'``.
        """),
        'vowel:': dict(
            description=r"""
            The DataFrame column which contains the vowel labels.
            If not given, defaults to ``'vowel'``.
        """),
        'formants:': dict(
            description=r"""
            The :class:`DataFrame` columns containing the formant data.
            If omitted, any columns matching
            ``'f0'``, ``'f1'``, ``'f2'``, ``'f3'``, ``'f4'``, or ``'f5'``
            will be used.
        """),
        'rename:': dict(
            description=r"""
            Rename output columns.
            If a :obj:`str` value, each output column will be
            renamed using that value with the characters ``{}``
            replaced by the original output column.
            If a :obj:`dict`, each output column will be renamed
            if it is key in the dictionary, with the corresponding
            value as the new name (or removed if that value is ``None``).
        """),
        'group_by:': dict(
            description=r"""
            One or more columns over which to group
            the data before normalization.
        """)
    },
    'type.other parameters': {
        'kwargs:': dict(
            parameter=r"""\*\*kwargs:""",
            description=r"""
            Optional keyword arguments passed to the parent constructor.
        """),
        'rename:': dict(
            description=r"""
            Rename output columns.
            See :ref:`renaming columns <normalization_renaming>`
            for details.
        """),
        'group_by:': dict(
            description=r"""
            One or more columns over which to group
            the data before normalization.
            See :ref:`grouping data <normalization_grouping>`
            for details.
        """)
    },
    'normalize': r"""
        Normalize formant data.

        Parameters
        ----------

        df:
            DataFrame containing formant data.

        **kwargs:
            Passed to the parent method.

        Returns
        -------
        :
            A DataFrame containing the normalized formants.
        """
}


def replace_parameter(parameter, replacement, indent):
    parameter = textwrap.dedent(replacement.get('parameter') or parameter)
    description = textwrap.dedent(replacement.get('description') or '').strip()
    lines = []
    if parameter:
        lines.append(parameter)
    if description:
        lines.extend(textwrap.indent(description, indent).split('\n'))
    return lines


PARAM_RE = r'^\s*([A-z0-9_ ,]+:)'
INDENT_RE = r'(\s*)'
UNDERLINE_RE = r'(\~+)|(-+)|(\=+)|(\^+)|(\.+)'

PATTERNS = [
    (PARAM_RE, replace_parameter)
]


def get_doc_indent(doc):
    """
    Return the initial whitespace
    """
    lines = doc.split('\n')
    indent = ''
    for line in lines:
        if line.strip():
            match = re.match(INDENT_RE, line)
            if match:
                indent = match.groups()[0]
        if indent:
            break
    return indent


def doc_sections(docs):
    """
    Iterate over the sections of a document.
    """
    lines = docs.split('\n')
    blank = 0
    section = []
    name = ''
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(re.match(INDENT_RE, line).groups()[0])
        is_section = i < len(lines) - 1 and re.match(UNDERLINE_RE, lines[i + 1]) is not None
        if is_section:
            yield name, section
            section = []
            name = line.strip()
            blank = 0
        if stripped:
            if name and blank >= 2 and indent == 0:
                yield name, section
                name = ''
                section = []
            blank = 0
        else:
            blank += 1
        section.append(line)
    if section:
        yield name, section


def dedent_docs(docs, indent=None):
    """
    Dedent docstring, optionally returning indent.
    """
    _indent = indent or get_doc_indent(docs)
    if not docs.startswith(_indent):
        docs = '\n' + _indent + docs
    if indent is not None:
        return textwrap.dedent(docs)
    return _indent, textwrap.dedent(docs)


def docstring(obj):
    obj_doc = obj.__doc__
    if obj_doc:
        docs = []
        indent, obj_doc = dedent_docs(obj_doc)
        for section, lines in doc_sections(obj_doc):
            section_lines = docstring_section(obj, section, lines, indent)
            if section.lower() == 'parameters':
                try:
                    name = obj.name
                    section_lines = [
                        'To use this normalizer in the :func:`vlnm.normalize` function, ',
                        "use ``method='{}'``.".format(name),
                        '',
                        ''
                    ] + section_lines
                except AttributeError:
                    pass
            docs.extend(section_lines)

        obj.__doc__ = textwrap.indent('\n'.join(docs), indent)
    else:
        if obj.__name__ in REPLACEMENTS:
            obj.__doc__ = REPLACEMENTS[obj.__name__]
    return obj


def docstring_section(obj, section, lines, indent):
    docs = []
    for line in lines:
        replaced = False
        for pattern, replacer in PATTERNS:
            match = re.match(pattern, line.strip())
            if match:
                key = match.groups()[0]
                context = type(obj).__name__.lower()
                if section:
                    context += '.{}'.format(section).lower()
                replacements = REPLACEMENTS.get(
                    context, REPLACEMENTS.get('default'))
                if replacements:
                    replacement = replacements.get(key)
                    if replacement:
                        docs.extend(replacer(key, replacement, indent))
                        replaced = True
                        break
        if not replaced:
            docs.append(line)
    return docs
