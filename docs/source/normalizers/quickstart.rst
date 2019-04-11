.. include:: ../defs.rst

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
in the first `cell`:

.. ipython::

    from vlnm import normalize

Normalizing a CSV file
----------------------

In perhaps the simplest case, |vlnm| can be used to normalize
a CSV file containing the vowel data.

So for example, given a CSV file
called :csv:`vowels.csv` as a comma separated file
with the columns :col:`speaker`, :col:`vowel`, :col:`f1` and :col:`f2`

.. ipython::
    :no-code:
    :path: {root}/source/_data

    with open('pb1952.csv', 'r') as file_in:
        for _ in range(6):
            print(next(file_in).strip())


Although it is worth noting, that in Jupyter
the file can be previewed a bit more prettily
using a |pandas| DataFrame:

.. ipython::
    :path: {root}/source/_data

    import pandas as pd
    pd.read_csv('pb1952.csv', nrows=5)


The file can be normalized according to :citet:`lobanov_1971`
and automatically saved to a new file :csv:`normalized.csv` as follows:

.. ipython::
    :code-only:

    normalize('vowels.csv', 'normalized.csv', method='lobanov')

This will create a file which starts with the following data:

.. ipython::
    :no-code:
    :path: {root}/source/_data

    import io
    df = pd.read_csv('pb1952.csv')
    norm_df = normalize(df, method='lobanov')
    stream = io.StringIO()
    norm_df.to_csv(stream, index=False, float_format='%g')
    #data = stream.getvalue()
    stream.seek(0)
    df = pd.read_csv(stream)
    stream.close()
    #lines = data.split('\n')
    #print('\n'.join(lines[:6]))
    df.head(5)

To save the normalized data to the same file, the second file name
can be omitted:

.. ipython::
    :code-only:

    normalize('vowels.csv', method='lobanov')

As this will overwrite the existing columns :col:`f1` and :col:`f2`
the normalized data can be written to new columns using the
:arg:`rename` argument:

.. ipython::
    :code-only:

    normalize('vowels.csv', method='lobanov', rename='{}_N')

This will create new columns :col:`f1_N` and :col:`f2_N` containing
the normalized data for the :col:`f1` and :col:`f2` columns,
respectively.

To change the separator used in the files the
:arg:`sep` argument can be used:

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





.. ipython::
    :path: {root}/source/_data

    import pandas as pd
    print(pd.read_csv('pb1952.csv', nrows=5))

Although in Jupyrer

.. ipython::
    :path: {root}/source/_data

    pd.read_csv('pb1952.csv', nrows=5)
