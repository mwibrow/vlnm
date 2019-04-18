.. include:: ../defs.rst

.. ipython::
    configure:
        dataframe:
            formatters:
                float64: '{:.05f}'
            index: yes
            dtypes:
                speaker: str
                vowel: str
        before: |
            import matplotlib
            matplotlib.use("agg")
            import pandas as pd
            from vlnm import normalize
        path: '{tmpdir}'
    hidden: yes

    Shell.copy(
        [Sphinx.confdir, '_data', 'pb1952.csv'],
        'pb1952.csv')
    df = pd.read_csv('pb1952.csv')
    df[['speaker', 'vowel', 'f1', 'f2']].to_csv('vowels.csv', index=False)

.. _section_normalization_quickstart:

Getting started
===============

There are a few ways in which |vlnm| can be used:

    - interactively in terminal (called the `command prompt` or `PowerShell` on Windows) running Python
    - non-interactively by running a Python script containing |vlnm| commands
    - interactively using a |Jupyter| notebook

By far the easiest way to use |vlnm| is the third option,
and for simplicity this is the method that is assumed below.
Having `installed Jupyter <https://jupyter.readthedocs.io/en/latest/install.html>`_
Python can be automatically run by
`starting a new notebook <https://jupyter.readthedocs.io/en/latest/running.html>`_
and |vlnm| can be imported by
`running code <https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Running%20Code.html>`_
in the first cell:

.. ipython::
    run: no

    import vlnm

Unless otherwise stated the data used in these examples
is based on :citet:`peterson_barney_1952` which
was extraced from :citet:`boersma_weenink_2018`.


Normalizing a CSV file
----------------------

In perhaps the simplest case, |vlnm| can be used to
normlize a CSV file containing the vowel data.
This CSV file could contain many columns, but for simplicity,
it is assumed the file has the columns
:col:`speaker`, :col:`vowel`, :col:`f1` and :col:`f2`.
The first few lines of the file can be previewed as
follows:

.. ipython::

    with open('vowels.csv') as csv_file:
        for i in range(6):
            print(next(csv_file), end='')


However, it is worth noting that in Jupyter,
CSV files can can be previewed a bit more prettily
using a |pandas| DataFrame:

.. ipython::

    import pandas as pd
    pd.read_csv('vowels.csv').head()


To normalize the formant data in this CSV file
the ``normalize`` function can be used, which
is imported using the following code:

.. ipython::

    from vlnm import normalize

To normalize the file :csv:`vowels.csv`
according to :citet:`lobanov_1971`
and automatically save to a new file :csv:`normalized.csv`,
the ``normalize`` function can be used.
This can be imported using the following code:


.. ipython::

    normalize('vowels.csv', 'normalized.csv', method='lobanov')

Which will produce a file ``normalized.csv`` including
the following data:

.. ipython::

    pd.read_csv('normalized.csv').head()

As this overwrites the existing
columns :col:`f1` and :col:`f2`,
the normalized data can be written to new columns using the
:arg:`rename` argument:

.. ipython::

    normalize('vowels.csv', 'normalized.csv', method='lobanov', rename='{}_N')
    pd.read_csv('normalized.csv').head()

This will create new columns :col:`f1_N` and :col:`f2_N` containing
the normalized data for the :col:`f1` and :col:`f2` columns,
respectively.


Finally, one (or both) of the file arguments can be a
`file object <https://docs.python.org/3/glossary.html#term-file-object>`_
created using the
`open() function <https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files>`_:


.. ipython::
    run: no

    with open('vowels.csv') as csv_in, open('normalized.csv', 'w') as csv_out:
        normalize(csv_in, csv_out, method='lobanov')

Normalizing a DataFrame
-----------------------

In many cases, some pre-processing of the CSV file could
be required, in which case it is easier to load the CSV
file

.. ipython::

    import pandas as pd
    df = pd.read_csv('vowels.csv')
    # Do something with the dataframe.
    ndf = normalize(df, method='lobanov')
    ndf.head()


Using |vlnm| Python classes
---------------------------


Tab-delmited and whitespace delimited files can be loaded by specifying the ``sep`` keyword
with ``sep=r'`t'`` for tab
Note that files are always saved as CSV files.
To save normalized data with a different delimiter

.. ipython::
    run: no
