"""
    Vowel plot artists.
    ~~~~~~~~~~~~~~~~~~~
"""
from typing import Dict

from matplotlib.lines import Line2D


class Artist:
    """Base class for plotting artists."""

    defaults = {}
    legend_defaults = {}

    prop_translator = {}
    legend_prop_translator = {}

    def __init__(self, defaults=None):
        self.defaults = defaults or self.__class__.defaults or {}

    def translate_props(self, props: Dict, translator: Dict = None) -> Dict:
        translator = translator or self.prop_translator
        translated = {}
        for prop, value in props.items():
            if prop in translator:
                translation = translator[prop]
                try:
                    translated.update(**translation(value))
                except TypeError:
                    if isinstance(translation, list):
                        translated.update(**{key: value for key in translation})
                    else:
                        while prop in translator:
                            prop = translator[prop]
                        if prop:
                            translated[prop] = value
            else:
                translated[prop] = value
        return translated

    def legend_artist(self, **_kwargs):  # pylint: disable=no-self-use
        """
        Return the artist to be used in legends.
        """

    def draw(self, *_args, **__kwargs):  # pylint: disable=no-self-use
        """
        Draw something.
        """


class MarkerArtist(Artist):

    defaults = {
        'marker': '.',
        'color': 'black',
        'size': 1
    }

    legend_defaults = {
        'marker': '.',
        'color': 'black',
        'size': 1
    }

    prop_translator = {
        'color': ['edgecolor', 'facecolor'],
        'size': 's'
    }

    legend_prop_translator = {
        's': 'markersize',
        'edgecolor': 'markeredgecolor',
        'facecolor': 'markerfacecolor',
        'linewidth': 'markeredgewidth',
        'markersize': None,
    }

    def legend_artist(self, **kwargs):
        """Return the legend artist for Markers."""
        props = self.legend_defaults.copy()
        props.update(**kwargs)
        props = self.translate_props(props)
        props = self.translate_props(props, self.legend_prop_translator)
        return Line2D(
            [0], [0], linestyle='', drawstyle=None, **props)

    def draw(self, axis, x, y, **kwargs):
        """Draw markers."""
        props = self.defaults.copy()
        props.update(**kwargs)
        props = self.translate_props(props)
        axis.scatter(x, y, **props)
