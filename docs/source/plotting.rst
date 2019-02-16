.. include:: defs.rst

Vowel Plots
===========

|vlnm| provides some convenience methods for creating
some of the common vowel plots seen in the literature.
However, it is a very thin wrapper around
the |matplotlib| plotting library, making more
advance customization of vowel plots possible.



.. plot::
   :figure: plot.figure
   :imports: import pandas as pd; from vlnm.plots import VowelPlot;

   ### df = pd.read_csv('source/_data/hawkins_midgely_2005.csv')
   relabel = dict(
       heed='i', hid='ɪ', head='ɛ', had='a', hard='ɑ',
       hoard='ɔ', heard='ɜ', hod='ɒ', hood='ʊ', whod='u', hud='ʌ')
   plot = VowelPlot().context(data=df, x='f2', y='f1', relabel=relabel)
   with plot:
        plot.markers(
            color_by='vowel', color='tab20', alpha=0.5, linewidth=0)
        plot.labels(label_by='vowel', color='black', where='mean')
        plot.set_xlabel('$f_2$ (Hz)')
        plot.set_ylabel('$f_1$ (Hz)')

Something else
