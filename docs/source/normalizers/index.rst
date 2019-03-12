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
Summmaries for each normalizer can be viewed
by clicking on the name in the **Normalizer** column.
The classification of normalizers according
to whether the calculations they perform are `intrinsic`
or `extrinsic` to certain properties
(i.e., vowel, formant, and speaker)
are taken for most normalizers
from :citet:`flynn_foulkes_2011`.

.. normalizers::


The following sections provide summaries for
each normalizer, grouped according to the
Python module in whih they are implemented.
Clicking on the class name for each normalizer
will show the API documentation for that normalizer,
with details regarding how to specify
parameters when using the normalizer.

It should be noted, that the module names
do not necessarily reflect the classification
of normalizers shown in the table above.

.. summaries::
