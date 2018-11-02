.. include:: defs.rst

Quick start
============

In the simplest case, you have a (possible large)
file containing formant data with columns for
`speaker`, `vowel`, `f1` and `f2` (data shown here
taken from :citealp:`hawkins_midgley_2005`):

.. csv-tabular::
    :file: ./_data/hawkins_midgely_2005.csv
    :header-rows: 1
    :rows: ..5, -5..


Assuming for the moment that this data is
in comma-separated (CSV) format in a file called `'input.csv'`,
to generate a new file called `'output.csv'`
containing formants normalized
using the normaliztion method of :citet:`lobanov_1971`,
you can simply use the `normalize` function:

.. console::
    :code-only:

    >>> from vlnm import normalize
    >>> normalize('input.csv', 'output.csv', method='lobanov')

Which will result in a CSV file including the following data:

.. csv-tabular::
    :file: ./_data/lobanov.csv
    :header-rows: 1
    :rows: ..6, -5..
    :truncate: 8

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