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
case `starting a new notebook <https://jupyter.readthedocs.io/en/latest/running.html>`_
will automatically start Python,
and |vlnm| can be imported by
`running code <https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Running%20Code.html>`_
in the first `cell`:

.. ipython::

    from vlnm import normalize

In the following examples, it is assumed that Jupyter notebook
is being used (it is *much* easier than trying to do things in a terminal).

Normalizing a CSV file
----------------------

In perhaps the simplest case, |vlnm| can be used to normalize
a CSV file containing the vowel data.

So for example, assuming a CSV file
called ``vowels.csv`` as a comma separated file
with the columns **speaker**, **vowel**, **f1** and **f2**,
such as:



The file can be normalized according to :citet:`lobanov_1971`
and automatically saved to a new file ``normalized.csv`` as follows:

.. ipython::
    :code-only:

    normalize('vowels.csv', 'normalized.csv', method='lobanov')

To save the normalized data to the same file, the second file name
can be omitted:

.. ipython::
    :code-only:

    normalize('vowels.csv', method='lobanov')

As this will overwrite the existing columns **f1** and **f2**
the normalized data can be written to new columns using the
``rename`` argument:

.. ipython::
    :code-only:

    normalize('vowels.csv', method='lobanov', rename='{}_N')

This will create new columns **f1_N** and **f2_N** containing
the normalized data for the **f1** and **f2** columns,
respectively.

To change the separator used in the files the
``sep`` argument can be used:

.. ipython::
    :code-only:

    normalize('vowels.tsv', 'normalized.tsv', method='lobanov', sep='\t')

Finally, one (or both) of the file arguments can be a
`file object <https://docs.python.org/3/glossary.html#term-file-object>`_
created using the
`open() function <https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files>`_:

.. ipython::
    :code-only:

    with open('vowels.csv', 'r') as file_in:
        with open('normalized.csv', 'w') as file_out:
            normalize(file_in, file_out, method='lobanov')



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
    vlnm.list_normalizers()
