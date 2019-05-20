"""
    Vowel plot artists.
    ~~~~~~~~~~~~~~~~~~~
"""
from typing import Dict

from matplotlib.lines import Line2D
import matplotlib.patches as mpatches


def dict_diff(this, that):
    """Return the keys in one dictionary that are not in another."""
    return {key: value for key, value in this.items() if not key in that}


class Artist:
    """Base class for plotting artists."""

    defaults = {}
    translators = {}

    def __init__(self, defaults=None):
        self.defaults = defaults or self.__class__.defaults or {}

    def _get_translator(self, which='plot'):
        return self.translators.get(which, self.translators.get('plot', {}))

    def _get_defaults(self, which='plot'):
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

    def legend(self, **_kwargs):  # pylint: disable=no-self-use
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
            'size': 1
        }
    )

    translators = dict(
        plot={
            'color': ['edgecolor', 'facecolor'],
            'size': 's'
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

    def legend(self, **props):
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

    def legend(self, **props):
        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))
        return mpatches.Polygon(
            xy=[(0.25, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0)],
            **props)

    def draw(self, axis, x, y, hull=False, closed=False, **props):

        translator = self._get_translator('legend')
        defaults = self.translate_props(self._get_defaults('legend'), translator)
        props = self.translate_props(props, translator)
        props.update(**dict_diff(defaults, props))

        props['closed'] = closed

        # xy = []
        # iterator = self._group_iterator(context)

        # mpl_props = {
        #     'color': ['edgecolor', 'facecolor'],
        #     'line': 'linestyle'
        # }
        # for axis, group_df, props, group_props in iterator:

        #     props = translate_props(props, mpl_props)

        #     xy = []
        #     if hull:
        #         group_x = group_df[context['x']].groupby(vertex).apply(np.mean)
        #         group_y = group_df[context['y']].groupby(vertex).apply(np.mean)
        #         convex_hull = MultiPoint(
        #             map(tuple, zip(group_x, group_y))).convex_hull
        #         xy.extend([(x, y) for x, y in convex_hull.coords])
        #     else:
        #         for vert in enumerate(vertices):
        #             i = group_df[vertex] == vert
        #             group_x = group_df[i, context['x']].mean()
        #             group_y = group_df[i, context['y']].mean()
        #             xy.append((group_x, group_y))

        #     polygon = mpatches.Polygon(
        #         xy=xy,
        #         **props)
        #     axis.add_patch(polygon)

        #     axis.relim()
        #     axis.autoscale_view()

        #     if legend:
        #         def _artist(**props):
        #             props = translate_props(props, mpl_props)
        #             return mpatches.Polygon(
        #                 xy=[(0.25, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0)],
        #                 **props)

        #         self._update_legend(legend, group_props, _artist)
        #     return self
