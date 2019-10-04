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
        return cls
    cls.__new__ = new
    return cls


def bind(bindable: Callable, to='__call__') -> Callable:
    """Bind a callable to a class method (default `__call__`)."""
    def wrapper(cls: Generic[U]) -> Generic[U]:
        def call(obj, *args, **kwargs):
            try:
                getattr(super(obj.__class__, obj), to)(*args, **kwargs)
            except AttributeError:
                pass
            return bindable(obj, *args, **kwargs)
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

    @property
    def plot(self):
        return PlotElement._plot

    def __call__(self, *args, **kwargs):
        if not self.plot:
            raise ValueError('No active vowel plot')


@singleton
class VowelPlotPlotElement(PlotElement):

    def __call__(self, *args, **kwargs):
        if PlotElement._plot:
            raise ValueError('Vowel plots cannot be nested')
        PlotElement._plot = VowelPlot(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        plot = PlotElement._plot
        plot.legend()
        figure = plot.figure
        PlotElement._plot = None
        return figure


@singleton
@bind(VowelPlot.markers)
class MarkersPlotElement(PlotElement):
    pass


@singleton
@bind(VowelPlot.labels)
class LabelsPlotElement(PlotElement):
    pass


@singleton
@bind(VowelPlot.legend)
class LegendPlotElement(PlotElement):
    pass


@singleton
@bind(VowelPlot.ellipses)
class EllipsesPlotElement(PlotElement):
    pass


@singleton
@bind(VowelPlot.contour)
class ContourPlotElement(PlotElement):
    pass


@singleton
@bind(VowelPlot.polygon)
class PolygonPlotElement(PlotElement):
    pass


# pylint: disable=invalid-name
vowelplot = VowelPlotPlotElement()
lables = LabelsPlotElement()
markers = MarkersPlotElement()
ellipses = EllipsesPlotElement()
contour = ContourPlotElement()
polygon = PolygonPlotElement()
