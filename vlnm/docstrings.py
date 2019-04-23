"""
Module for inserting common documentation snippits into docstrings.
"""
import re
import textwrap


SUBSTITUTIONS = {
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
    ('kwargs:', 'type'): dict(
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
            If a :obj:`dict`, each output column will be reanmed
            if it is key in the dictionary, with the corresponding
            value as the new name (or removed if that value is ``None``).
        """),
    'groups:': dict(
        description=r"""
            One or more Dataframe columns over which to group
            the data before applying the normalizer.
        """)
}

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


PARAM_RE = r'^\s*([A-z0-9_ ,]+:)'


def get_doc_indent(doc):
    lines = doc.split('\n')
    indent = ''
    for line in lines:
        if line.strip():
            match = re.match(r'(\s+)', line)
            if match:
                indent = match.groups()[0]
        if indent:
            break
    return indent


def docstring(obj):
    context = type(obj).__name__
    obj_doc = obj.__doc__
    if obj_doc:
        docs = []
        indent = get_doc_indent(obj_doc)
        if not obj_doc.startswith(indent):
            obj_doc = '\n' + indent + obj_doc

        lines = textwrap.dedent(obj_doc).split('\n')
        for line in lines:

            match = re.match(PARAM_RE, line)
            if match:
                key = match.groups()[0]
                replacement = SUBSTITUTIONS.get(
                    (key, context),
                    SUBSTITUTIONS.get(
                        (key, None),
                        SUBSTITUTIONS.get(key)))
                if replacement:
                    docs.extend(replace_parameter(key, replacement, indent))
                    continue

            docs.append(line)
            # key = match.groups()[0]
            # replacement = REPLACEMENTS.get(
            #     (key, context),
            #     REPLACEMENTS.get(
            #         (key, None),
            #         REPLACEMENTS.get(key)))
            # if replacement:
            #     if replacement.strip().startswith(key):
            #         docs = docs[:-1]
            #         replacement = replacement.strip()
            #     if docs[-1].strip().startswith('kwargs'):
            #         docs[-1] = docs[-1].replace('kwargs', r'\*\*kwargs')
            #     docs.extend(replacement.split('\n'))
        if obj.__name__.endswith('Normalizer'):
            try:
                name = obj.name
                docs.extend([
                    'To use this normalizer in the :func:`vlnm.normalize` function, ',
                    'use ``method=\'{}\'``:'.format(name),
                    '',
                    '.. ipython::',
                    '    run: no',
                    '',
                    '    from vlnm import normalize',
                    "    normalize('vowels.csv', 'normalized.csv', method='{}')".format(
                        name),
                    ''])
            except AttributeError:
                pass
        obj.__doc__ = textwrap.indent('\n'.join(docs), indent)
        # if 'bigham' in obj.__name__.lower():
        #     print(obj.__doc__)

    else:
        if obj.__name__ in REPLACEMENTS:
            obj.__doc__ = REPLACEMENTS[obj.__name__]
    return obj


def replace_parameter(parameter, replacement, indent):
    parameter = textwrap.dedent(replacement.get('parameter') or parameter)
    description = textwrap.dedent(replacement.get('description') or '').strip()
    lines = []
    if parameter:
        lines.append(parameter)
    if description:
        lines.extend(textwrap.indent(description, indent).split('\n'))
    return lines
