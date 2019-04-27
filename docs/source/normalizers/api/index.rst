.. include:: ./defs.rst

.. _section_normalization_api:

API
===

Modules
~~~~~~~

Below, links are provided to documentation for the lower level
programming interface provided by |vlnm|.

Normalizers are often classified according to whether
the calculations they perform are `intrinsic`
or `extrinsic` to certain properties (i.e.,
vowel, formant and speaker --- see e.g., :citealp:`flynn_foulkes_2011`).

The normalizers have been implemented in modules whose names
might suggest some correspondence to the most prominent `intrinsic` property
as described by the literature, but this is mostly
coincidental: normalizers have been logically
grouped according to 'programmatical convenience',
so the names of the modules should not be taken to
indiciate any accepted classification of normalizers in the literature.

:mod:`vlnm`
-----------------------
.. toctree::
   :maxdepth: 1

   vlnm

:mod:`vlnm.registration`
------------------------
.. toctree::
   :maxdepth: 1

   registration

:mod:`vlnm.conversion`
----------------------
.. toctree::
   :maxdepth: 1

   conversion

:mod:`vlnm.normalizers`
-----------------------
.. toctree::
   :maxdepth: 1

   base
   centroid
   decomposition
   formant
   gender
   speaker
   vowel
