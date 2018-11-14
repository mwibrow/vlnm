"""
Module for inserting common documentation snippits into docstrings.
"""

REPLACEMENTS = dict(
    speaker=r"""
    speaker: :obj:`str`
        The DataFrame column which contains the speaker labels.
        If not given (or overridden in the `normalize` method)
        defaults to ``'speaker'``.
    """,
    vowel=r"""
    vowel: :obj:`str`
        The DataFrame column which contains the vowel labels.
        If not given (or overridden in the `normalize` method)
        defaults to ``'vowel'``.
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
