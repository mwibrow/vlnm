.. include:: defs.rst

VLNM: Vowel normalization using Python
======================================

|license| |build status| |coverage|

What is VLNM?
-------------

|vlnm| is a |python| package, primarily aimed at phoneticians
who need to normalize vowel data
(i.e., reduce variation in acoustic features due to speaker characteristics)
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
in :citet:`flynn_foulkes_2011`, plus a few other
methods that can be found in the literature.
Each normalizer is described in the documentation
for :ref:`section_normalization`.


.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contents
   :titlesonly:

   installation
   normalizers/index
   Datasets <data>
   license
   bibliography
