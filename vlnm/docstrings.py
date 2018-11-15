"""
Module for inserting common documentation snippits into docstrings.
"""

REPLACEMENTS = dict(
    f0=r"""
    f0 : :obj:`str` | :obj:`list`
        The DataFrame column which contains the :math:`F_0` data.
        If not given, defaults to ``'f0'``.
    """,
    f1=r"""
    f1 : :obj:`str` | :obj:`list`
        The DataFrame column which contains the :math:`F_1` data.
        If not given, defaults to ``'f1'``.
    """,
    f2=r"""
    f2 : :obj:`str` | :obj:`list`
        The DataFrame column which contains the :math:`F_2` data.
        If not given, defaults to ``'f2'``.
    """,
    f3=r"""
    f3 : :obj:`str` | :obj:`list`
        The DataFrame column which contains the :math:`F_3` data.
        If not given, defaults to ``'f3'``.
    """,
    formants=r"""
    formants : :obj:`list`
        A list of DataFrame columns which contains the formant data.
        If not given, defaults any DataFrame columns found in the list
        ``['f0', 'f1', 'f2', 'f3]``.
    """,
    speaker=r"""
    speaker: :obj:`str`
        The DataFrame column which contains the speaker labels.
        If not given, defaults to ``'speaker'``.
    """,
    vowel=r"""
    vowel: :obj:`str`
        The DataFrame column which contains the vowel labels.
        If not given, defaults to ``'vowel'``.
    """,
    rename=r"""
    rename: :obj:`str`
        If given, rename output columns according to the
        specified pattern. The characters ``{}`` will
        be replaced with the default output column,
        so using ``rename='{}_N'`` will suffix all
        output columns with ``_N``.
    """,
    kwargs=r"""
    **kwargs
        Other keyword arguments passed to the parent class.
    """,
    normalized_data=r"""
    `pandas.DataFrame`
        The normalized data.
    """)

def docstring(cls):
    """Decorator for replacing docstrings."""

    docs = cls.__doc__
    for key, value in REPLACEMENTS.items():
        docs = docs.replace(r'{{'+key+r'}}', value.strip())
    cls.__doc__ = docs
    return cls
