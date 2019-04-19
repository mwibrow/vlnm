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
was extraced from PRAAT :citep:`boersma_weenink_2018`.


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


Instead of passing file names to the :func:`normalize` function,
one (or both) of the arguments can be a
`file object <https://docs.python.org/3/glossary.html#term-file-object>`_
created using the
`open() function <https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files>`_:

.. ipython::
    run: no

    with open('vowels.csv') as csv_in, open('normalized.csv', 'w') as csv_out:
        normalize(csv_in, csv_out, method='lobanov')


Renaming columns
^^^^^^^^^^^^^^^^
By default, most normalizers will happily overwrite
existing formant columns. If the original columns
should be retained,
the normalized data can be written to new columns using the
:arg:`rename` argument:

.. ipython::

    normalize('vowels.csv', 'normalized.csv', method='lobanov', rename='{}_N')
    pd.read_csv('normalized.csv').head()

This will create new columns :col:`f1_N` and :col:`f2_N` containing
the normalized data for the :col:`f1` and :col:`f2` columns,
respectively.

Tab and whitespace delimited files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tab-delmited and whitespace delimited files can be normalzied by
using the ``sep`` keyword:

.. ipython::
    run: no

    # Tab-delimited columns
    normalize('vowels.csv', 'normalized.csv', sep=r'\t', method='lobanov')

    # Whitespace delimited columns
    normalize('vowels.csv', 'normalized.csv', sep=r'\s+', method='lobanov')

Note that files will always be saved as comma separated files.
If greater flexibility is required saving (or loading)
vowel data, then the data should be loaded into
a |Pandas| Dataframe as shown below
(this is actually what |vlnm| does internally).

Passing arguments to a normalizer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Arguments can be passed to a normalizer using addition keyword
arguments in the :func:`normalizer` function.
For example, the :class:`LobanovNormalizer` class
assumes the speaker labels are
in a column named :col:`speaker`.
If the speaker labels are in a different column,
for example, :col:`Talker` then this can be passed
to the normalizer as follows:

.. ipython::
    run: no

    normalize('vowels.csv', 'normalized.csv', method='lobanov', speaker='Talker')

Keyword arguments for each normalizer are described
in the :ref:`section_normalization_api`.



Normalizing a DataFrame
-----------------------

In many cases, some pre-processing of the CSV file could
be required, in which case it is easier to load the CSV
file into a Dataframe using the ``read_csv`` function from the
|Pandas| package. This provides considerably more
flexibility regarding the file format, along
with selection of columns, handling of null values and so on
(for details see the Pandas `documentation <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html>`_).

To normalize the formant data in the Dataframe,
simply pass the variable containing the data
to the first argument of the :func:`normalize` function:

.. ipython::

    import pandas as pd # If this hasn't been imported before.
    df = pd.read_csv('vowels.csv')
    norm_df = normalize(df, method='lobanov')

The file can be saved using the
``to_csv`` method:

.. ipython::

    norm_df.to_csv('normalized.csv', index=False)

(Note that ``index=False`` is added to avoid the row numbers
saved to the file, along witht the normalized data.)



Using |vlnm| Python classes
---------------------------

The :func:`normalize` function is a wrapper around
the normalizer classes. For example,
|vlnm| recognizes that the argument ``method='lobanoc'``
corresponds to the :class:`LobanovNormalizer` class.

It is perfectly possibly to use these classes directly
and it may be easier to do so, if comparing several
normalizers. To use the class it must be imported
first and instantiated. All normalizer classes
have a ``normalize`` method whose first argument
is a Dataframe:

.. ipython::

    from vlnm import LobanovNormalizer

    norm = LobanovNormalizer(rename='{}_N')
    df = pd.read_csv('vowels.csv')
    norm_df = norm.normalize(df)
    norm_df.head()
