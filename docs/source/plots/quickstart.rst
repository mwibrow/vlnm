.. include:: ../defs.rst

Quickstart
==========

|vlnm| provides some convenience methods for creating
some of the common 2-dimensional vowel plots seen in
the literature.
However, it is a very thin wrapper around
the |matplotlib| plotting library, making more
advance customization of vowel plots possible.


|vlnm| does not provide a single 'kitchen sink' function
for producing different types of vowel plots but allows
the user to 'compose' a vowel plot from elements
including markers, labels, ellipses, polygons and arrows,
as well as providing access to the underlying |matplotlib|
axes API.

Markers
-------

.. ipython::

    from vlnm import pb1952
    from vlnm.plotting import VowelPlot

    df = pb1952(columns=['vowel', 'f1', 'f2'])

    with VowelPlot(data=df, x='f2', y='f1') as plot:
        plot.markers(color_by='vowel', color='tab20', size=5, legend='markers')
        plot.legend('markers')
        plot.xlabel('F2 (Hz)')
        plot.ylabel('F1 (Hz)')


.. ipython::

    from vlnm import pb1952
    from vlnm.plotting import VowelPlot

    df = pb1952(columns=['vowel', 'f1', 'f2'])

    with VowelPlot(data=df, x='f2', y='f1') as plot:
        plot.ellipses(color_by='vowel', color='tab20', legend='ellipses')
        plot.legend('ellipses')
