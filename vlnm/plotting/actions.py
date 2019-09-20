"""
Convenience functions
"""
from typing import Union, Dict
from contextlib import contextmanager
from functools import wraps

import pandas as pd

from .plots import VowelPlot, get_plot


def require_vowel_plot(func):
    @wraps(func)
    def wrapper(*args, plot=None, **kwargs):
        plot = plot or get_plot()
        if not plot:
            raise ValueError('No plot is currently active.')
        return func(_plot=plot, *args, **kwargs)
    return wrapper


def vowel_plot(**kwargs):
    return VowelPlot(**kwargs)


@require_vowel_plot
def markers(*args, **kwargs):
    """Add markers to an existing plot.

    Parameters
    ----------

    See the documentation for the :method:`VowelPlot.markers` method.

    Example
    -------

    ipython::

        with VowelPlot(data=df, x='f2', y='f1'):
            markers(color_by='vowel', color='tab20')


    """
    plot = kwargs.pop('_plot')
    plot.markers(*args, **kwargs)


@require_vowel_plot
def labels(*args, **kwargs):
    plot = kwargs.pop('_plot')
    plot.labels(*args, **kwargs)


@require_vowel_plot
def ellipses(*args, **kwargs):
    plot = kwargs.pop('_plot')
    plot.ellipses(*args, **kwargs)


@require_vowel_plot
@contextmanager
def legend(**kwargs):
    plot = kwargs.pop('_plot')
    legend_options = plot.legend_options
    try:
        plot.legend_options.update(**kwargs)
        yield plot
    finally:
        plot.legend_options = legend_options


@require_vowel_plot
@contextmanager
def subplot(**kwargs):
    plot = kwargs.pop('_plot')
    try:
        plot.subplot(**kwargs)
        yield plot
    finally:
        pass


@require_vowel_plot
@contextmanager
def data(
        data: Union[str, pd.DataFrame] = None,
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
