.. include:: defs.rst

Quick start
============

Although, some normalizers have more complex requirements,
in the simplest case, you have a CSV file which contains columns
for `speaker`, `vowel`, `f1` and `f2`:

.. console::
    ###
    import os
    import pandas
    pandas.set_option('display.max_columns', None)
    read_csv = pandas.read_csv
    def read_csv_alt(filename, *args, **kwargs):
        return read_csv(os.path.join('source', '_data', filename), *args, **kwargs)

    pandas.read_csv = read_csv_alt
    ###
    >>> from vlnm.normalizers import LobanovNormalizer
    >>> import pandas as pd
    >>> df = pd.read_csv('hawkins_midgely_2005.csv')
    >>> df.head(n=5)
    >>> df_norm = LobanovNormalizer().normalize(df)
    >>> df_norm.head(n=5)
    ###
    pandas.read_csv = read_csv
    ###

Perhaps, you wish to keep the original formant values, in
which case the `rename` keyword argument can be used:

.. console::
    ###
    from vlnm.normalizers import LobanovNormalizer
    import os
    import pandas as pd
    df = pd.read_csv('source/_data/hawkins_midgely_2005.csv')
    ###
    >>> df_norm = LobanovNormalizer().normalize(df, rename='{}\'')
    >>> df_norm.head(n=5)



End