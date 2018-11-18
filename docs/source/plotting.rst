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

   import matplotlib
   import matplotlib.pyplot as plt
   import seaborn as sns
   import pandas as pd

   plt.figure(figsize=(4,4))
   df = pd.read_csv('_data/hawkins_midgely_2005.csv')
   ax = sns.scatterplot(df['f2'], df['f1'], hue=df['vowel'], linewidth=0, alpha=0.5)
   ax.invert_xaxis()
   ax.invert_yaxis()
   ax.set_xlabel('$F_2$ (Hz)')
   ax.set_ylabel('$F_1$ (Hz)')

   plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., frameon=False)

