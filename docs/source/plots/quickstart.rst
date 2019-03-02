.. include:: ../defs.rst

Quickstart
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


.. code::

    from engine import RunForrestRun

    """Test code for syntax highlighting!"""

    class Foo:
        def __init__(self, var):
            self.var = var
            self.run()

        def run(self, arg=4, arg2='four', *args, **kwargs):
            RunForrestRun()  # run along!

        @staticmethod
        def stop(self):
            print('\'escaped\'')
            print(f'{formatted}!')


    foo = Foo()
    foo2 = Foo()
    bah = foo.stop()
    bar2 = foo2.stop()

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
