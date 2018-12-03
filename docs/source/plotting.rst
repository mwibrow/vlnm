.. include:: defs.rst

Vowel Plots
===========

|vlnm| provides some convenience methods for creating
some of the common vowel plots seen in the literature.
However, it is a very thin wrapper around
the |matplotlib| plotting library, making more
advance customization of vowel plots possible.


.. plot::

   ### import matplotlib
   ### matplotlib.use('agg')
   import pandas as pd
   from vlnm.plots import VowelPlot
   df = pd.read_csv('source/_data/hawkins_midgely_2005.csv')
   plot = VowelPlot(data=df, x='f2', y='f1', vowel='vowel')
   with plot:
        plot.markers(alpha=0.5, legend=True)
        plot.set_xlabel('$f_2$ (Hz)')
        plot.set_ylabel('$f_1$ (Hz)')
   ### __figure__ = plot.figure

Something else
