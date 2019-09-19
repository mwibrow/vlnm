"""
Convenience functions
"""

from contextlib import contextmanager
from functools import wraps

import pandas as pd

from .plots import VowelPlot, get_plot


def vowel_plot(func):
    @wraps(func)
    def wrapper(*args, plot=None, **kwargs):
        plot = plot or get_plot()
        if not plot:
            raise ValueError('No plot is currently active.')
        return func(_plot=plot, *args, **kwargs)
    return wrapper


@vowel_plot
def markers(*args, **kwargs):
    """Add markers to an existing plot.

    Parameters
    ----------

    See the documentation for the :method:`VowelPlot.markers` method.

    Example
    -------

    ipython::

        with VowelPlot():
            with data(data=df, x='f2', y='f1'):
                markers(color_by='vowel', color='tab20')


    """
    plot = kwargs.pop('_plot')
    plot.markers(*args, **kwargs)


@vowel_plot
def labels(*args, **kwargs):
    plot = kwargs.pop('_plot')
    plot.labels(*args, **kwargs)


@vowel_plot
def ellipses(*args, **kwargs):
    plot = kwargs.pop('_plot')
    plot.ellipses(*args, **kwargs)


@vowel_plot
@contextmanager
def legend(**kwargs):
    plot = kwargs.pop('_plot')
    legend_options = plot.legend_options
    try:
        plot.legend_options.update(**kwargs)
        yield plot
    finally:
        plot.legend_options = legend_options


@vowel_plot
@contextmanager
def data(
        data: Union[str, pd.DataFrame, File] = None,
        x: str = 'f2',
        y: str = 'f1', **kwargs):
    plot = kwargs.pop('_plot')
    context = dict(
        data=plot.plot_context.get('data'),
        x=plot.plot_context.get('x'),
        y=plot.plot_context.get('y'),
    )
    try:
        plot.plot_context.update(
            data=data,
            x=x,
            y=y,
        )
        yield plot
    finally:
        plot.plot_context.update(**context)
