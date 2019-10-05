"""
Module `elements`
~~~~~~~~~~~~~~~~~

This module contains convenience functions
to faciliate use of the :class:`VowelPlot` class.
"""

from typing import Callable, Generic, TypeVar

from vlnm.plotting import VowelPlot

T = TypeVar('T')  # pylint: disable=invalid-name
U = TypeVar('U')  # pylint: disable=invalid-name


def singleton(cls: Generic[T]) -> Generic[T]:
    """Singleton decorator."""
    instance = '_instance'
    setattr(cls, instance, None)

    def new(cls: Generic[T], *args, **kwargs) -> Generic[T]:
        if getattr(cls, instance) is None:
            setattr(cls, instance, object.__new__(cls, *args, **kwargs))
        return getattr(cls, instance)
    cls.__new__ = new
    return cls


def bind(bindable: Callable, instance=None, to='__call__') -> Callable:
    """Bind a callable to an instance method (default `__call__`)."""
    def wrapper(cls: Generic[U]) -> Generic[U]:
        def call(obj, *args, **kwargs):
            try:
                getattr(super(obj.__class__, obj), to)(*args, **kwargs)
            except AttributeError:
                pass
            if instance:
                return getattr(instance(), bindable.__name__)(*args, **kwargs)
            return bindable(*args, **kwargs)
        setattr(cls, to, call)
        return cls
    return wrapper


class PlotElement:
    """
    Base class for plot elements.

    A plot 'element' is anything that can be drawn
    in a vowel plot (including the vowel plot itself).
    """

    _plot: VowelPlot = None

    @classmethod
    def get_plot(cls):
        return PlotElement._plot

    @classmethod
    def set_plot(cls, plot):
        PlotElement._plot = plot

    def __call__(self, *args, **kwargs):
        if not PlotElement._plot:
            raise ValueError('No active vowel plot')


def get_plot():
    return PlotElement.get_plot()


def set_plot(plot=None):
    PlotElement.set_plot(plot)


def bind_vowelplot_method(bindable: Callable):
    return bind(bindable, get_plot)


@singleton
class VowelPlotPlotElement(PlotElement):

    def __call__(self, *args, **kwargs):
        self.begin(*args, **kwargs)

    def begin(self, *args, **kwargs):
        if get_plot():
            raise ValueError('Vowel plots cannot be nested')
        set_plot(VowelPlot(*args, **kwargs))
        return self

    def end(self):  # pylint: disable=no-self-use
        plot = get_plot()
        plot.legend()
        figure = plot.figure
        set_plot()
        return figure

    def __enter__(self):
        return self.begin()

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        return self.end()


@singleton
class DataPlotElement(PlotElement):

    def __call__(self, *args, **kwargs):
        super().__call__()
        settings = get_plot().settings
        settings.push(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        settings = get_plot().settings
        return settings.pop()


@singleton
@bind_vowelplot_method(VowelPlot.markers)
class MarkersPlotElement(PlotElement):
    pass


@singleton
@bind_vowelplot_method(VowelPlot.labels)
class LabelsPlotElement(PlotElement):
    pass


@singleton
@bind_vowelplot_method(VowelPlot.legend)
class LegendPlotElement(PlotElement):
    pass


@singleton
@bind_vowelplot_method(VowelPlot.ellipses)
class EllipsesPlotElement(PlotElement):
    pass


@singleton
@bind_vowelplot_method(VowelPlot.contour)
class ContourPlotElement(PlotElement):
    pass


@singleton
@bind_vowelplot_method(VowelPlot.polygon)
class PolygonPlotElement(PlotElement):
    pass


# pylint: disable=invalid-name
vowelplot = VowelPlotPlotElement()
data = DataPlotElement()
lables = LabelsPlotElement()
markers = MarkersPlotElement()
ellipses = EllipsesPlotElement()
contour = ContourPlotElement()
polygon = PolygonPlotElement()
