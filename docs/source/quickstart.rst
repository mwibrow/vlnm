.. include:: defs.rst

Quick start
============

Although, some normalizers have more complex requirements,
in the simplest case, you have a CSV file which contains columns
for `speaker`, `vowel`, `f1` and `f2`:

.. csv-tabular::
    :file: ./_data/hawkins_midgely_2005.csv
    :header-rows: 1
    :pre-rows: 5
    :post-rows: 5

If this file is called, for example, `input.csv`

.. console::
    :code-only:

    >>> from vlnm import normalize
    >>> normalize('input.csv', 'output.csv', method='lobanov')


|VLNM| provides a :code:`read_csv` function
(which is actually a super-thin wrapper around the |Pandas|
:code:`read_csv` function) for reading CSVs,
which can be used to read the CSV file.

The the :code:`normalize` function from |vlnm| can be used:

.. console::

    ### import os
    ### import vlnm
    ### vlnm.DATA_DIR = os.path.join(__file__, '_data')
    >>> from vlnm import read_csv, normalize
    >>> df = read_csv('hawkins_midgely_2005.csv')
    >>> df.head(n=5) ### dataframe
    >>> df_norm = normalize(df, method='lobanov')
    >>> df_norm.head(n=10) ### dataframe

Perhaps, you wish to keep the original formant values, in
which case the `rename` keyword argument can be used:

.. console::

    ### import os
    ### import vlnm
    ### vlnm.DATA_DIR = os.path.join(__file__, '_data')
    ### from vlnm import read_csv, normalize
    ### df = read_csv('hawkins_midgely_2005.csv')
    >>> df_norm = normalize(df, method='lobanov', rename='{}_N')
    >>> df_norm.head(n=5) ### dataframe



End