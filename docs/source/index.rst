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


.. plot::

   import matplotlib
   import matplotlib.pyplot as plt
   import numpy as np

   # Data for plotting
   t = np.arange(0.0, 2.0, 0.01)
   s = 1 + np.sin(2 * np.pi * t)

   plt.plot(t, s)
   plt.plot(t, s / 2)



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |build status| image:: https://travis-ci.org/mwibrow/vlnm.svg?branch=master
    :target: https://travis-ci.org/mwibrow/vlnm

.. |coverage| image:: https://coveralls.io/repos/github/mwibrow/vlnm/badge.svg
    :target: https://coveralls.io/github/mwibrow/vlnm
