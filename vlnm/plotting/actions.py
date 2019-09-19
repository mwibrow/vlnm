from contextlib import contextmanager
from functools import wraps


from .plots import get_plot


def vowel_plot(func):
    @wraps(func)
    def wrapper(*args, plot=None, **kwargs):
        plot = plot or get_plot()
        if not plot:
            raise ValueError('No plot')
        return func(plot, *args, **kwargs)
    return wrapper


@vowel_plot
def markers(plot, *args, **kwargs):
    plot.markers(*args, **kwargs)


@vowel_plot
def labels(plot, *args, **kwargs):
    plot.labels(*args, **kwargs)


@vowel_plot
@contextmanager
def legend(plot, **kwargs):
    legend_options = plot.legend_options
    try:
        plot.legend_options = kwargs
        yield plot
    finally:
        plot.legend_options = legend_options


@vowel_plot
@contextmanager
def data(plot, data=None, x=None, y=None):
    context_data = plot.plot_context.get('data')
    context_x = plot.plot_context.get('x')
    context_y = plot.plot_context.get('y')
    try:
        plot.plot_context['data'] = data
        plot.plot_context['x'] = x
        plot.plot_context['y'] = y
        yield plot
    finally:
        plot.plot_context['data'] = context_data
        plot.plot_context['x'] = context_x
        plot.plot_context['y'] = context_y
