.. include:: defs.rst

Quick start
============

Although, some normalizers have more complex requirements,
in the simplest case, you have a CSV file which contains columns
for `speaker`, `vowel`, `f1` and `f2`.

The csv file must be loaded using the |Pandas|
:code:`read_csv` function, and then the
:code:`normalize` function from |vlnm| can be used:

.. console::
    ###
    import os
    import vlnm
    vlnm.DATA_DIR = os.path.join(__file__, '_data')
    ###
    >>> from vlnm import read_csv, normalize
    >>> df = read_csv('hawkins_midgely_2005.csv')
    >>> df.head(n=5)
    >>> df_norm = normalize(df, method='lobanov')
    >>> df_norm.head(n=5)

Perhaps, you wish to keep the original formant values, in
which case the `rename` keyword argument can be used:

.. console::
    ###
    from vlnm import read_csv, normalize
    df = read_csv('hawkins_midgely_2005.csv')
    ###
    >>> df_norm = normalize(df, method='lobanov', rename='{}_N')
    >>> df_norm.head(n=5)



End