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

    from vlnm import pb1952

    df = pb1952(['speaker', 'vowel', 'f1', 'f2'])
    df.to_csv('vowels.csv', index=False)

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


.. _normalization_renaming:

Renaming columns
^^^^^^^^^^^^^^^^
By default, most normalizers will happily overwrite
existing formant columns. If the original columns
should be retained,
the normalized data can be written to new columns using the
:arg:`rename` argument.
The value passed to this argument can take two forms.
In the first, a simple string can be passed,
and if it contains the characters ``{}``, they will be replaced by the
original output columns:

.. ipython::

    normalize('vowels.csv', 'normalized.csv', method='lobanov', rename='{}*')
    pd.read_csv('normalized.csv').head()

This will create new columns :col:`f1*` and :col:`f2*` containing
the normalized data for the :col:`f1` and :col:`f2` columns,
respectively.

If the string does not contain the characters ``{}``,
the normalized columns will be numbered using the string
as a prefix, so using ``rename='n'`` will produce
normalized columns :col:`n1`, :col:`n2`… and so on:

.. ipython::

    normalize('vowels.csv', 'normalized.csv', method='lobanov', rename='n')
    pd.read_csv('normalized.csv').head()

Alternatively, the :arg:`rename` argument can be a dictionary.
Columns will be renamed only if they have a key in the
dictionary, and will take the name of the corresponding value,
unless that value is ``None`` in which case the column
will be removed:

.. ipython::

    rename = {'f1': 'norm1', 'f2': None}
    normalize('vowels.csv', 'normalized.csv', method='lobanov', rename=rename)
    pd.read_csv('normalized.csv').head()

.. _normalization_grouping:

Grouping data
^^^^^^^^^^^^^

In rare cases, perhaps when using a speaker extrinsic normalizer
which relies on population level calculations
(e.g., :citealp:`nordstrom_1977`)
with different populations (e.g., children and adults) in the
same data set, it is necessary to consider these populations
seperately as different groups.
In thses cases the ``groupby`` parameter can be used to group
data over one or more columns and normalize each group separately:

.. ipython::
    run: no

    rename = {'f1': 'norm1', 'f2': None}
    normalize('vowels.csv', 'normalized.csv', method='lobanov', groupby='type')
    pd.read_csv('normalized.csv').head()

It is worth noting that this is almost identical to the following code:

.. ipython::
    run: no

    import pandas as pd
    from vlnm import LobanovNormalizer

    normalizer = LobanovNormalizer()
    df = pd.read_csv('vowels.csv')
    norm_df = df.groupby('type', as_index=False).apply(normalizer.normalize)
    norm_df = norm_df.reset_index(drop=True)
    norm_df.to_csv('normalized.csv', index=False)

Although ``groupby`` can be used with most normalizers,
it only usually makes sense to used it with speaker extrinsic
normalizers.

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


Alternative column names
^^^^^^^^^^^^^^^^^^^^^^^^

All normalizers assume the formant data is in
columns :col:`f0`, :col:`f1`, :col:`f2`, … and so on,
that is a lower case `f` followed by a number.
For basic use cases, if the formant columns are not named
in this fashion it is trivial to rename the columns
prior to normalization using the :meth:`pandas.DataFrame.rename`
method.

In some cases, however, particularly when there are
multiple measurements for a particular formant across
a single vowel, it will be necessary to explictly
state which columns contain the formant data.

|vlnm| has two different ways of specifying formant
columns, depending on whether the normalizer
is `formant generic` or `formant specific`.
For example, the :class:`BarkNormalizer` class
(``method='bark'``) is a formant generic
normalizer: it only needs to know which columns contain
any formant data, and normalizes them `en masse`.
By contrast the :class:`BighamNormalizer` class
(``method='bigham'``), constructs 'derived' vowels
from :math:`F_1` and :math:`F_2` formants, so needs
to know which columns correspond specifically
to the :math:`F_1` and :math:`F_2` formants; this
class is a `formant specific` normalizer.
It is important to note that this distinction bears no relation to
the classification of normalizers as being 'formant intrinsic'
or 'formant extrinsic' (see e.g., :citealp:`flynn_foulkes_2011`):
this merely represents a more logical
grouping based on programming convenience.


Formant generic normalizers
"""""""""""""""""""""""""""

As formant generic normalizers don't need to know
what the individual formants are, a list of all formants
is sufficient. These normalizers take a ``formants``
parameter and to explictly indicate which columns contain formant data
the ``formants`` parameter can take a list of columns:

.. ipython::

    formants=['f1@20', 'f1@50', 'f1@80', 'f2@20', 'f2@50', 'f2@80']

Alternatively, it is possible to use a
`regular expression <https://docs.python.org/3/howto/regex.html>`_
to compactly specify multiple formants.
For example, the following matches exactly the columns specified
above:

.. ipython::

    formants=r'f[12]@[258]0'

Formant specific normalizers
""""""""""""""""""""""""""""

As formant specific normalizers need to know which
columns contain specific formants, these normalizers
require parameters ``f0``, ``f1``, ``f2``, and so on
(the exact parameters may differ depending on the normalizer).
Each parameter takes a list of formants:


.. ipython::
    run: no

    f1=['f1@20', 'f1@50', 'f1@80'], f2=['f2@20', 'f2@50', 'f2@80']


Again, a regular expression can be used instead of a list,
but it is important to note that the column names for each formant
will be sorted as case-sensitive strings after collecting all
columns matching the regular expression.

.. ipython::
    run: no

    f1=r'f1@[258]0', f2=r'f2@[258]0'




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
saved to the file, along with the normalized data).



Using |vlnm| Python classes
---------------------------

The :func:`normalize` function is a wrapper around
the normalizer classes. For example,
|vlnm| recognizes that the argument ``method='lobanov'``
corresponds to the :class:`LobanovNormalizer` class.

It is perfectly possibly to use these classes directly
and it may be easier to do so, if comparing several
normalizers. To use the class it must be imported
first and instantiated. All normalizer classes
have a ``normalize`` method whose first argument
is a Dataframe:

.. ipython::

    from vlnm import LobanovNormalizer

    norm = LobanovNormalizer(rename='{}*')
    df = pd.read_csv('vowels.csv')
    norm_df = norm.normalize(df)
    norm_df.head()
