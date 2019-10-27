"""
    Vowel plot artists.
    ~~~~~~~~~~~~~~~~~~~
"""
from typing import Any, Dict, Tuple

from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib import rcParams

from vlnm.plotting.arrows import FancierArrowPatch


def dict_diff(this, that):
    """Return the entries in one dictionary that are not in another."""
    return {key: value for key, value in this.items() if not key in that}


class Artist:
    """Base class for plotting artists."""

    defaults = {}
    translators = {}

    def __init__(self, defaults=None, vowel_plot=None):
        self.vowel_plot = vowel_plot
        self.defaults = defaults or self.__class__.defaults or {}

    def _get_translator(self, which='plot'):  # pragma: no cover
        return self.translators.get(which, self.translators.get('plot', {}))

    def _get_defaults(self, which='plot'):  # pragma: no cover
        return self.defaults.get(which, self.defaults.get('plot', {}))

    def translate_props(self, props: Dict, translator: Dict) -> Dict:
        translated = {}
        for prop, value in props.items():
            if prop in translator:
                translation = translator[prop]
                try:
                    _translated = self.translate_props(translation(value), translator)
                    translated.update(**_translated)
                except TypeError:
                    if isinstance(translation, list):
                        _translated = self.translate_props(
                            {key: value for key in translation if value}, translator)
                        translated.update(**_translated)
                    else:
                        while prop in translator:
                            prop = translator[prop]
                        if prop:
                            translated[prop] = value
            else:
                translated[prop] = value
        return translated

    def _get_props(self, props, name):  # pragma: no cover
        translator = self._get_translator(name)
        defaults = self.translate_props(self._get_defaults(name), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        return props

    def _get_legend_props(self, props):  # pragma: no cover
        return self._get_props(props, 'legend')

    def _get_plot_props(self, props):  # pragma: no cover
        return self._get_props(props, 'plot')

    def legend(self, **_kwargs) -> Any:  # pylint: disable=no-self-use
        """
        Return the artist to be used in legends.
        """

    def plot(self, *_args, **__kwargs):  # pylint: disable=no-self-use
        """
        Draw something.
        """


class MarkerArtist(Artist):

    defaults = dict(
        plot={
            'marker': '.',
            'color': 'black',
            'size': rcParams['lines.markersize'],
        }
    )

    translators = dict(
        plot={
            'color': ['edgecolor', 'facecolor'],
            'size': lambda s: {'s': s ** 2}
        },
        legend={
            'color': ['markeredgecolor', 'markerfacecolor'],
            'size': 'markersize',
            's': 'markersize',
            'edgecolor': 'markeredgecolor',
            'facecolor': 'markerfacecolor',
            'linewidth': 'markeredgewidth',
            'markersize': None,
        }
    )

    def legend(self, **props) -> Line2D:
        """Return the legend artist for Markers."""
        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        return Line2D(
            [0], [0], linestyle='', drawstyle=None, **props)

    def plot(self, axis, x, y, **props):
        """Draw markers."""
        translator = self._get_translator('plot')
        defaults = self.translate_props(self._get_defaults('plot'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        axis.scatter(x, y, **props)


class PolygonArtist(Artist):

    defaults = dict(
        plot=dict(
            color='black',
            line='-'
        )
    )

    translators = dict(
        plot={
            'color': ['edgecolor', 'facecolor'],
            'line': 'linestyle'
        }
    )

    def legend(self, **props) -> mpatches.Patch:
        """Return the artist to be used in the legend.
        """
        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        return mpatches.Polygon(
            xy=[(0.25, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0)],
            **props)

    def plot(self, axis, xy, **props):
        """Plot a ploygon."""
        translator = self._get_translator('plot')
        defaults = self.translate_props(self._get_defaults('plot'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))

        polygon = mpatches.Polygon(
            xy=xy,
            **props)
        axis.add_patch(polygon)


class EllipseArtist(Artist):
    """Class for plotting ellipses.
    """

    defaults = dict(
        plot=dict(
            facecolor='none',
            edgecolor='black',
            linestyle='-',
        ))

    translators = dict(
        plot={
            'color': ['edgecolor', 'facecolor'],
            'line': 'linestyle'
        })

    def legend(self, **props) -> mpatches.Patch:
        props = self._get_legend_props(props)
        return mpatches.Ellipse(
            xy=(0.5, 0.5),
            width=1,
            height=0.625,
            angle=0,
            **props)

    def plot(self, axis, xy: Tuple[int, int], width: float, height: float, angle: float, **props):
        props = self._get_plot_props(props)
        ellipse = mpatches.Ellipse(
            xy=xy,
            width=width,
            height=height,
            angle=angle,
            **props)
        axis.add_patch(ellipse)


class LabelArtist(Artist):
    """Artist class for drawing labels."""
    defaults = dict(
        plot={
            'color': 'black',
            'size': 10,
            'ha': 'center',
            'va': 'center',
        }
    )

    translators = dict(
        plot={}
    )

    def legend(self, **_) -> None:
        """Return the legend artist for labels."""
        return None

    def plot(self, axis, x, y, labels, **props):
        """Draw markers."""
        props = self._get_plot_props(props)
        if isinstance(labels, str) and labels:
            for lx, ly in zip(x, y):
                axis.text(lx, ly, labels, clip_on=True, **props)
        else:
            for lx, ly, label in zip(x, y, labels):
                axis.text(lx, ly, label, clip_on=True, **props)


class ContourArtist(Artist):

    defaults = dict(
        plot=dict(
            color='black',
            line='-'
        )
    )

    translators = dict(
        plot={
            'line': 'linestyle'
        }
    )

    def legend(self, **props) -> mpatches.Patch:
        """Return the artist to be used in the legend.
        """
        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        return mpatches.Polygon(
            xy=[(0.25, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0)],
            **props)

    def plot(self, axis, x, y, z, **props):
        """Plot a Contour."""
        translator = self._get_translator('plot')
        defaults = self.translate_props(self._get_defaults('plot'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))

        axis.contour(x, y, z, **props)


class LineArtist(Artist):

    defaults = dict(
        plot=dict(
            color='black',
            line='-'
        )
    )

    translators = dict(
        plot={
            'scale': 'mutation_scale'
        }
    )

    def legend(self, **props) -> mpatches.Patch:
        """Return the artist to be used in the legend.
        """
        arrows = props.pop('arrows', (None, None))
        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))

        path = Path(
            vertices=[(0, 0.5), (1, 0.5)],
            codes=[Path.MOVETO] + [Path.LINETO])

        start_arrow, end_arrow = arrows
        return arrows.FancierArrowPatch(
            path=path,
            snap=True,
            arrowstyle=mpatches.ArrowStyle(
                'fancier',
                begin=start_arrow,
                end=end_arrow,
            ),
            **props)

    def plot(self, axis, points, **props):
        """Plot a Contour."""

        arrows = props.pop('arrows', (None, None))
        translator = self._get_translator('plot')
        defaults = self.translate_props(self._get_defaults('plot'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))

        codes = [Path.MOVETO] + [Path.LINETO] * (len(points) - 1)
        path = Path(
            vertices=points,
            codes=codes)

        start_arrow, end_arrow = arrows
        arrow = arrows.FancierArrowPatch(
            path=path,
            snap=True,
            arrowstyle=mpatches.ArrowStyle(
                'fancier',
                begin=start_arrow,
                end=end_arrow,
            ),
            **props)

        axis.add_patch(arrow)
