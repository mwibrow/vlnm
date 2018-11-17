"""
Module for inserting common documentation snippits into docstrings.
"""
import re

REPLACEMENTS = dict(
    f0=r"""
    f0 :
        The DataFrame column which contains the :math:`F_0` data.
    """,
    f1=r"""
    f1 :
        The DataFrame column which contains the :math:`F_1` data.
    """,
    f2=r"""
    f2 :
        The DataFrame column which contains the :math:`F_2` data.
    """,
    f3=r"""
    f3 :
        The DataFrame column which contains the :math:`F_3` data.
    """,
    formants=r"""
    formants :
        A list of DataFrame columns which contains the formant data.
        If not given, the normalizer will use
        any DataFrame columns found in the list
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
    rename:
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
    """,
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
    Normalize formant data in a DataFrame.

        Parameters
        ----------
        df :
            The formant data to normalize.

        Other parameters
        ----------------
        :
            For other parameters see the documentation for the constructor.

        Returns
        -------
        :
            The normalized data.
    """)


WSP_RE = re.compile(r'^(\s*)')

def reindent(text, indent=0):
    """Reindint a multi line string."""
    lines = text.split('\n')
    while not lines[0]:
        lines = lines[1:]
    while not lines[-1]:
        lines = lines[-1:]
    whitespace = [len(WSP_RE.match(line).group(1))
                  for line in lines]
    min_indent = min(
        space for line, space in zip(lines, whitespace) if line.strip())
    reindented = []
    for i, line in enumerate(lines):
        if line.strip() and whitespace[i] > 0:
            line = re.sub(
                r'^\s+', ' ' * (whitespace[i] - min_indent + indent), line)
        reindented.append(line)
    return '\n'.join(reindented)


SUBS_RE = re.compile(r'^(\s*)\{%([^%]+)%\}')

def docstring(obj):
    """Replace element in docstrings."""
    lines = obj.__doc__.split('\n')
    docs = []
    for line in lines:
        match = SUBS_RE.match(line)
        if match:
            indent, key = match.groups()
            key = key.strip()
            replacement = REPLACEMENTS.get(key)
            if replacement:
                line = reindent(replacement, indent=len(indent))
        docs.append(line)
    obj.__doc__ = '\n'.join(docs)
    return obj
