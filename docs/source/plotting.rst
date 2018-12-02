.. include:: defs.rst

Vowel Plots
===========

It is hoped that in the future |vlnm| will provide a dedicated
API for producing vowel plots in Python simply and easily.
Until then, the following sections describe a series
of 'recipies' for producing and customising various
types of vowel plots using |matplotlib|.


.. plot::

   ### import matplotlib
   ### matplotlib.use('agg')
   import pandas as pd
   from vlnm.plots import VowelPlot
   df = pd.read_csv('source/_data/hawkins_midgely_2005.csv')
   plot = VowelPlot(data=df, x='f2', y='f1', vowel='vowel')
   with plot:
        plot.markers(alpha=0.5, legend=True)
   ### __figure__ = plot.figure

Something else
