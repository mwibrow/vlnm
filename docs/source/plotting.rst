.. include:: defs.rst

Vowel Plots
===========

It is hoped that in the future |vlnm| will provide a dedicated
API for producing vowel plots in Python simply and easily.
Until then, the following sections describe a series
of 'recipies' for producing and customising various
types of vowel plots using |matplotlib|.

.. console::
   :script:
   :code-only:

   from matplotlib import pyplot as plt
   import pandas as pd
   import os
   df = pd.read_csv('_data/hawkins_midgely_2005.csv')
   plt.scatter(df['f1'], df['f2'])


.. plot::

   import pandas as pd
   df = pd.read_csv('_data/hawkins_midgely_2005.csv')
   plot = VowelPlot(
      data=df, x='f2', y='f1', vowel='vowel', alpha=0.5)
   with plot:
      plot.markers()
      plot.labels(which='mean')

