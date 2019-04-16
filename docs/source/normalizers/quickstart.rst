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
in the first `cell`:


Normalizing a CSV file
----------------------

In perhaps the simplest case, |vlnm| can be used to normalize
a CSV file containing the vowel data.

So for example, given a CSV file
called :csv:`vowels.csv` as a comma separated file
with the columns :col:`speaker`, :col:`vowel`, :col:`f1` and :col:`f2`,
which starts with the following data:


.. ipython::

    from vlnm import preview
    preview('vowels.csv', n=6)


.. ipython::

    from vlnm import normalize
    normalize('vowels.csv', 'normalized.csv', method='lobanov')

Which will produce a file ``normalized.csv`` including
the following data:

.. ipython::

    preview('normalized.csv', n=6)


Although it is worth noting, that in Jupyter
the file can be previewed a bit more prettily
using a |pandas| DataFrame:



The file can be normalized according to :citet:`lobanov_1971`
and automatically saved to a new file :csv:`normalized.csv` as follows:


This will create a file which starts with the following data:



To save the normalized data to the same file, the second file name
can be omitted:



As this will overwrite the existing columns :col:`f1` and :col:`f2`
the normalized data can be written to new columns using the
:arg:`rename` argument:



This will create new columns :col:`f1_N` and :col:`f2_N` containing
the normalized data for the :col:`f1` and :col:`f2` columns,
respectively.

To change the separator used in the files the
:arg:`sep` argument can be used:



Finally, one (or both) of the file arguments can be a
`file object <https://docs.python.org/3/glossary.html#term-file-object>`_
created using the
`open() function <https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files>`_:




Normalizing a DataFrame
-----------------------


Using |vlnm| Python classes
---------------------------
