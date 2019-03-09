.. include:: ../defs.rst

.. _section_normalization:

Vowel Normalization
===================

.. toctree::
   :maxdepth: 2
   :caption: Normalization Contents
   :hidden:

   quickstart
   api

|vlnm| Provides a comprehensive range of normalizers
(see section :ref:`section_normalizers` below) that have been
described in the literature (although remains agnostic
regarding which may be considered the most suitable
for a given collection of formant data).

To just get started using normalizers, jump to
:ref:`section_normalization_quickstart`.
More detailed descriptions of the implementation
(including links to the source code)
can be found in the :ref:`section_normalization_api`.


.. _section_normalizers:

Normalizers
-----------

|vlnm| implements the normalizers shown below.
The documentation for each normalizer can be viewed
by clicking on the relevance class name
in the **Python class** column.
The classification of normalizers according
to whether the calculations they perform are `intrinsic`
or `extrinsic` to certain properties
(i.e., vowel, formant, and speaker)
are taken from :citet:`flynn_foulkes_2011`.

.. normalizers::
