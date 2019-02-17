.. include:: defs.rst

Vowel Plots
===========

|vlnm| provides some convenience methods for creating
some of the common vowel plots seen in the literature.
However, it is a very thin wrapper around
the |matplotlib| plotting library, making more
advance customization of vowel plots possible.


|vlnm| does not provide a single 'kitchen sink' function
for producing different types of vowel plots but allows
the user to 'compose' a vowel plot from elements
including markers, labels, ellipses, polygons and arrows,
as well as providing access to the underlying |matplotlib|
axes API.

Plot context
------------

Plot elements like markers, lables and so on, are
added to a plot within a particular plotting 'context'.
This context can provided options common to all
plot elements, such as common data source
and column names for formant data.

.. code::

    plot = VowelPlot()
    plot.begin()
    plot.context(data=df, x='f2', y='f1')
    # Plot elements...
    plot.end()

The ``begin()`` and ``end()`` methods are required and are used
to prepare and finalise the |matplotlib| backend, respectively.

Conviniently, preparing and finalising the plot and setting the context
can be handled by a Python
`context manager <https://docs.python.org/3/library/stdtypes.html#typecontextmanager>`_,
using the python `with <https://docs.python.org/3/reference/compound_stmts.html#with>`_
statement:

.. code::

    plot = VowelPlot()
    with plot(data=df, x='f2', y='f1'):
       # Plot elements...

However, the plot context can be overridden for individual elements as required:

.. code::

    plot = VowelPlot()
    with plot(data=df, x='f2', y='f1', color_by='vowel'):
        # Use default context:
        plot.markers()
        # Use custom context:
        plot.markers(x='f2_N', y='f1_N', color='black')
        # ...other elements

Markers
-------

To add markers to a plot, the `markers` method can be used.

.. plot::
   :figure: plot.figure
   :imports: import pandas as pd; from vlnm.plots import VowelPlot;

   ### df = pd.read_csv('source/_data/hawkins_midgely_2005.csv')
   plot = VowelPlot()
   with plot(data=df, x='f2', y='f1'):
        plot.markers(color_by='vowel', color='tab20')
        plot.set_xlabel('$f_2$ (Hz)')
        plot.set_ylabel('$f_1$ (Hz)')


By adding `legend=True` to the

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
            color_by='vowel', color='tab20', alpha=0.5, marker='o', markerfacecolor='none')
        plot.labels(label_by='vowel', color='black', where='mean', size=10)
        plot.set_xlabel('$f_2$ (Hz)')
        plot.set_ylabel('$f_1$ (Hz)')

Something else
