"""
Module for inserting common documentation snippits into docstrings.
"""
import re

REPLACEMENTS = dict(
    hz_to_bark=r"""
    Parameters
    ----------
    frq:
        A numpy array-compatible data structure
        (e.g., ``numpy.ndarray``, ``pandas.DataFrame``, etc.).

    Returns
    -------
    Array-like
        The frequency data on the Bark scale.
    """,
    normalize=r"""
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
    """)

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
    'formants:': r"""
        The :class:`DataFrame` columns containing the formant data.
        If omitted, any columns matching ``'f0'``, ``'f1'``, …,
        ``'f5'``, that are in the DataFrame will be used.
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
    ('__init__', 'kwargs:'): r"""
        Optional keyword arguments passed to the parent constructor.
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


def docstring(obj):
    context = type(obj).__name__
    if obj.__doc__:
        docs = []

        lines = obj.__doc__.split('\n')
        state = None
        for line in lines:
            docs.append(line)
            match = re.match(PARAM_RE, line)
            if match:
                key = match.groups()[0]
                replacement = REPLACEMENTS.get(
                    (key, context),
                    REPLACEMENTS.get(
                        (key, None),
                        REPLACEMENTS.get(key)))
                if replacement:
                    if replacement.strip().startswith(key):
                        docs = docs[:-1]
                    if docs[-1].strip().startswith('kwargs'):
                        docs[-1] = docs[-1].replace('kwargs', r'\*\*kwargs')
                    docs.extend(replacement.split('\n'))
        if obj.__name__.endswith('Normalizer'):
            try:
                name = obj.name
                docs.extend([
                    '    .. note::',
                    '        To use this normalizer in the :func:`normalize` function, ',
                    '        use ``method=\'{}\'``.'.format(name),
                    ''])
            except AttributeError:
                pass
        obj.__doc__ = '\n'.join(docs)
    else:
        if obj.__name__ in REPLACEMENTS:
            obj.__doc__ = REPLACEMENTS[obj.__name__]
    return obj
