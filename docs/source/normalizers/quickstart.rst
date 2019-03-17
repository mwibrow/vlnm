.. include:: ../defs.rst

.. _section_normalization_quickstart:

Getting started
===============

|vlnm| can be used in a terminal (called the `command prompt`
or `PowerShell` on Windows) running a Python process.
This is what starting Python in a terminal on MacOS might look like:

.. code::

    $ python
    Python 3.7.2 (default, Feb 25 2019, 09:00:08)
    [Clang 10.0.0 (clang-1000.11.45.5)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from vlnm import normalize
    >>>

Alternatively, |vlnm| may be used from a Jupyter notebook, in which
case starting a new notebook will automatically start Python.

.. ipython

    from vlnm import normalize

Normalizing a CSV file
----------------------

In perhaps the simplest case, |vlnm| can be used to normalize
a CSV file containing


.. ipython::
    :code-only:

    normalize('vowels.csv', 'normalized.csv', method='lobanov')

.. ipython::
    :code-only:

    with open('vowels.csv', 'r') as file_in,
            open('normalized.csv', 'w') as file_out:
        normalize(file_in, file_out, method='lobanov')

.. ipython::
    :code-only:

    normalize('vowels.csv', 'normalized.csv', method='lobanov', sep='\t')

Normalizing a DataFrame
-----------------------

.. ipython::
    :code-only:

    import pandas as pd
    df = pd.read_csv('vowels.csv')
    norm_df = normalize(df, method='lobanov', rename='{}_N')
    norm_df.head()

Using |vlnm| Python classes
---------------------------

.. ipython::
    :code-only:

    import vlnm
    norm = vlnm.get_normalizer('lobanov')
    norm_df = norm(df, rename='{}_N')
    norm_df.head()

.. ipython::

    import vlnm
    print(vlnm.list_normalizers())

