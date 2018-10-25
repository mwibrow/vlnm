Welcome to VLNM's documentation!
================================================

:Release: |release|
:Date:    |today|

|build status| |coverage|

Vowel normalization in python.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart


:citet:`flynn_foulkes_2011a`

:citet:`e.g., {% flynn_foulkes_2011a %}`

:citet:`{% flynn_foulkes_2011a %}, chap.2`

:citet:`e.g., {% flynn_foulkes_2011a %}, chap.2`

:citet:`e.g., {% flynn_foulkes_2011a, adank_etal_2004 %}, chap.2`

:citep:`flynn_foulkes_2011a`

:citep:`e.g., {% flynn_foulkes_2011a %}`

:citep:`{% flynn_foulkes_2011a %}, chap.2`

:citep:`e.g., {% flynn_foulkes_2011a %}, chap.2`

:citep:`e.g., {% flynn_foulkes_2011a, adank_etal_2004 %}, chap.2`

.. bibliography:: bibliography.bib
    :style: author-year



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |build status| image:: https://travis-ci.org/mwibrow/vlnm.svg?branch=master
    :target: https://travis-ci.org/mwibrow/vlnm

.. |coverage| image:: https://coveralls.io/repos/github/mwibrow/vlnm/badge.svg
    :target: https://coveralls.io/github/mwibrow/vlnm
