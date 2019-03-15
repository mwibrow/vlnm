.. include:: defs.rst

VLNM: Vowel normalization and plotting using Python
===================================================

:Release: |release|
:Date:    |today|

.. ipython::

    import pandas as pd
    df = pd.DataFrame(dict(a=[1,2,3],b=[4,5,6]))


.. ipython::

    import pandas as pd
    df = pd.DataFrame(dict(a=[1,2,3],b=[4,5,6]))
    print('hello')

.. ipython::

    import pandas as pd
    df = pd.DataFrame(dict(a=[1,2,3],b=[4,5,6]))
    print('hello')
    df

.. ipython::

    import pandas as pd
    df = pd.DataFrame(dict(a=[1,2,3],b=[4,5,6]))
    pnt

What is VLNM?
-------------

|vlnm| is a |python| package, primarily aimed at phoneticians
who need to normalize vowel data
(i.e., reduce variation in acoustic features due to speaker characteristics)
and produce graphical representations of vowel data
for sociophonetic research.

Using VLNM
----------

After installing (see the section on :ref:`section_installation` for details),
|vlnm| can used in as part of any Python programme or script,
however to get get started quickly it is probably easiest
to use |jupyter| to create 'notebooks' which enable
easy editing of Python code, inspecting and manipulating
of vowel data, and the display of vowel plots.


Vowel normalization
^^^^^^^^^^^^^^^^^^^

|vlnm| provides all of the normalization methods described
in :citet:`flynn_foulkes_2011`.
Each normalizer is described in the documentation
for :ref:`section_normalization` and can be used
to normalize vowel data


Vowel plots
^^^^^^^^^^^

|vlnm| provides a relatively thin wrapper around
|matplotlib| to make producing some of the vowel plots
found in the literature easier to produce than
using Matplotlib alone.


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents
   :titlesonly:

   installation
   normalizers/index
   plots/index
   license
   bibliography
