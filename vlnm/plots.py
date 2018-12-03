"""

This module provides some convenience functions
for producing the more common vowel plots found in the literature.

All the functionality implemented in this module
forms a very thin wrapper around
the |matplotlib| library, and advanced customation of vowel
plots will require familiarity with |matplotlib|.
"""

import os
from typing import Dict, List, Tuple, Union

from matplotlib.axes import Axes
from matplotlib.colors import Colormap, ListedColormap
from matplotlib.cm import get_cmap
from matplotlib.figure import Figure
from matplotlib import Path
from matplotlib.font_manager import FontProperties
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as st


# pylint: disable=C0103
Color = Union[str, Tuple[float, float, float, float]]
Colors = Union[List[Color], ListedColormap]
Marker = Union[str, Tuple[int, int, int], List[Tuple[float, float]], Path]
Markers = List[Marker]
Font = Union[str, FontProperties]
Fonts = List[Font]

FIGURE_KWARGS = dict(
    num=None,
    figsize=None,
    dpi=None,
    facecolor=None,
    edgecolor=None,
    frameon=True,
    FigureClass=Figure,
    clear=False)

def _create_figure(*args, **kwargs):
    return plt.figure(*args, **kwargs)

class VowelPlot(object):
    """Class for managing vowel plots.

    Parameters
    ----------
    data:
        DataFrame containing the formant data.
    x:
        The DataFrame column which contains the x-coordinates.
    y:
        The DataFrame column which contains the y-coordinates.
    vowel:
        The DataFrame column which contains the vowel categories/labels.
    color:
        Colors to be used for each vowel category.
        This will be converted into a list of colors
        which will be recycled if there are more vowels
        than colors.
    marker:
        Marks to be used for each vowel category.
        This will be converted into a list of marks
        which will be recycled if there are more vowels
        than marks.
    width:
        Width of the figure in inches.
    height:
        Height of the figure in inches.
    rows:
        Number of rows in the figure (for subplots).
    columns:
        Number of columns in the figure (for subplots).

    Other Parameters
    ----------------
    Other parmaeters are passed to the constructor of
    :py:class:`matplotlib.figure.Figure`.

    """

    def __init__(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = 'f2',
            y: Union[str, int] = 'f1',
            vowel: Union[str, int] = 'vowel',
            color: Union[Color, Colors] = 'tab20',
            font: Union[Font, Fonts] = None,
            marker: Union[Marker, Markers] = '.',
            width: str = None,
            height: str = None,
            rows: str = 1,
            columns: str = 1,
            **kwargs):

        figsize = (width, height) if width and height else None
        self.figure = _create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.params = dict(
            x=x, y=y, vowel=vowel, color=color, font=font, marker=marker)
        self.data = data
        self.axis = None

    def subplot(self, index: int = None) -> Axes:
        """Get the axis for a subplot."""
        axes = self.figure.get_axes()
        if len(axes) < self.rows * self.columns:
            self.axis = self.figure.add_subplot(
                self.rows, self.columns, len(axes) + 1)
        else:
            self.axis = axes[index or 0]
        return self.axis

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, *_args):
        self.end()

    def begin(self):
        """Set up the plot."""
        if not self.axis:
            self.axis = self.subplot()

    def end(self):
        """Finalise the plot."""
        axes = self.figure.get_axes()
        for axis in axes:
            if not axis.xaxis_inverted():
                axis.invert_xaxis()
            if not axis.yaxis_inverted():
                axis.invert_yaxis()

    def markers(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            vowel: Union[str, int] = None,
            color: Union[Color, Colors] = None,
            marker: Union[Marker, Markers] = None,
            #
            which: str = 'all',
            legend: bool = False,
            size: float = None,
            **kwargs):
        """Add markers to the vowel plot.

        Parameters
        ----------

        data:
            DataFrame containing the formant data.
        x:
            The DataFrame column which contains the x-coordinates.
        y:
            The DataFrame column which contains the y-coordinates.
        vowel:
            The DataFrame column which contains the vowel categories/labels.
        which:
            One of:
                - ``'all'``: all rows in the DataFrame will be used.
                - ``'mean'``: The means for each category will be used.
                - ``'median'``: The medians for each category will be used.
            If ``'mean'`` or ``'median'``, the ``mapping``
            parameter needs to specify the `vowel` mapping.
        legend:
            Whether to add the markers to the legend.
            Will be ignored if labels are used as markers.
        color:
            Colors to be used for each vowel category.
            This will be converted into a list of colors
            which will be recycled if there are more vowels
            than colors.
        markers:
            Marks to be used for each vowel category.
            This will be converted into a list of marks
            which will be recycled if there are more vowels
            than marks.
        size:
            Size of markers.
        """

        params = dict(
            x=x or self.params.get('x'),
            y=y or self.params.get('y'),
            vowel=vowel or self.params.get('vowel'),
            color=color or self.params.get('color'),
            marker=marker or self.params.get('marker'))

        vowel = params['vowel']
        df = data if data is not None else self.data
        x = params['x']
        y = params['y']
        if which == 'mean':
            df = df.groupby(vowel, as_index=True).apply(
                lambda group_df: group_df[[x, y]].mean(axis=0))
            df = df.reset_index()
        elif which == 'median':
            df = df.groupby(vowel, as_index=True).apply(
                lambda group_df: group_df[[x, y]].median(axis=0))
            df = df.reset_index()

        vowels = sorted(df[vowel].unique())
        color_map = get_color_map(params['color'], vowels)

        marker_map = get_marker_map(params['marker'] or '.', vowels)
        grouped = df.groupby(vowel, as_index=False)

        # Remove the matplotlib keys that this method handles.
        kwargs.pop('c', None)
        kwargs.pop('cmap', None)
        kwargs.pop('s', None)

        for key, group_df in grouped:
            marker = marker_map.get(key, '')
            color = color_map.get(key)
            if legend:
                kwargs['label'] = key
            self.axis.scatter(
                group_df[x], group_df[y], s=size, c=[color], marker=marker,
                **kwargs)

        if legend:
            self.axis.legend()

    def labels(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            vowel: Union[str, int] = None,
            color: Union[Color, Colors] = None,
            font: Union[Font, Fonts] = None,
            which: str = 'all',
            **kwargs):
        """Add labels to the vowel plot.

        data:
            DataFrame containing formant data.
        x:
            The DataFrame column which contains the x-coordinates.
        y:
            The DataFrame column which contains the y-coordinates.
        vowel:
            The DataFrame column which contains the vowel categories/labels.
        which:
            One of:
                - ``'all'``: all rows in the DataFrame will be used.
                - ``'mean'``: The means for each category will be used.
                - ``'median'``: The medians for each category will be used.
            If ``'mean'`` or ``'median'``, the ``mapping``
            parameter needs to specify the `vowel` mapping.
        """
        params = dict(
            x=x or self.params.get('x'),
            y=y or self.params.get('y'),
            vowel=vowel or self.params.get('vowel'),
            color=color or self.params.get('color'),
            font=font or self.params.get('font'))

        vowel = params['vowel']
        df = data if data is not None else self.data
        x = params['x']
        y = params['y']
        if which == 'mean':
            df = df.groupby(vowel, as_index=True).apply(
                lambda group_df: group_df[[x, y]].mean(axis=0))
            df = df.reset_index()
        elif which == 'median':
            df = df.groupby(vowel, as_index=True).apply(
                lambda group_df: group_df[[x, y]].median(axis=0))
            df = df.reset_index()

        vowels = sorted(df[vowel].unique())
        color_map = get_color_map(color, vowels)
        font_map = get_font_map(font, vowels)

        # Remove the matplotlib keys that this method handles.
        kwargs.pop('fontproperties', None)
        kwargs.pop('horizontalalignment', None)
        kwargs.pop('verticalalignment', None)

        grouped = df.groupby(vowel, as_index=False)

        for key, group_df in grouped:
            color = color_map.get(key)
            font = font_map.get(key)
            for xy in zip(group_df[x], group_df[y]):
                self.axis.text(
                    xy[0], xy[1],
                    key,
                    color=color,
                    fontproperties=font,
                    horizontalalignment='center',
                    verticalalignment='center',
                    **kwargs)

    def ellipses(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            vowel: str = None,
            color: Union[Color, Colors] = None,
            confidence: float = 0.95,
            **kwargs):
        """Add confidence-interval-based ellipsed around formant data.

        Parameters
        ----------
        data:
            The DataFrame containing the formant data.
        x:
            The DataFrame column containing the x-coordinates of the data.
        y:
            The DataFrame column containing the y-coordinates of the data.
        vowel:
            The DataFrame column containing the vowel categories/labels.
        include:
            Labels of vowel labels to include in the plot.
            If not given, all vowels will be used.
        exclude:
            Vowel labels to exclude from the plot.
        colors:

        confidence:
            Confidence level (under the assumption that the data
            is normally distributed) to calculate the
            the percentile from the Chi-squared distribution.
            Values shoule be in the range :math:`0` to :math:`1`.

        Other parameters
        ----------------
            All other parameters are passed on to the constructor
            of the :class:`matplotlib.patches.Ellipse` constructor
            See the documentation for the `Ellipse class`__.

        .. _Ellipse: https://matplotlib.org/api/_as_gen/matplotlib.patches.Ellipse.html
        __ Ellipse _
        """
        params = dict(
            x=x or self.params.get('x'),
            y=y or self.params.get('y'),
            vowel=vowel or self.params.get('vowel'),
            color=color or self.params.get('color'))

        df = data or self.data
        x = params['x']
        y = params['y']
        vowel = params['vowel']

        grouped = df.groupby(vowel, as_index=False)
        for _, group_df in grouped:
            center_x, center_y, width, height, angle = get_confidence_ellipse(
                group_df[x], group_df[y], confidence)
            ellipse = mpatches.Ellipse(
                xy=(center_x, center_y),
                width=width,
                height=height,
                angle=angle,
                **kwargs)
            self.axis.add_artist(ellipse)

    def __getattr__(self, attr):
        if hasattr(self.axis, attr):
            return getattr(self.axis, attr)
        return object.__getattribute__(self, attr)

def get_confidence_ellipse(
        x: List[float],
        y: List[float],
        confidence: float = 0.95) -> Tuple[float, float, float]:
    """Calculate parameters for a 2D 'confidence ellipse'

    Parameters
    ----------
    x:
        Data for the x-coordinates.
    y:
        Data for the y-coordinates.
    confidence:
        Confidence level in the range :math:`0` to :math:`1`.

    Returns
    -------
    :
        A tuple the width, height, and angle (in degrees)
        of the required ellipse.
    """
    x = np.array(x)
    y = np.array(y)
    if x.size != y.size:
        raise ValueError('Ellipse data must be the same shape.')
    elif x.size < 3 or y.size < 3:
        raise ValueError('Too little data to calculate ellipse')
    cov = np.cov(x, y)
    eigenvalues, eignvectors = np.linalg.eig(cov)
    angle = np.arctan2(*np.flip(eignvectors[:, 0])) / np.pi * 180
    alpha = st.chi2(df=2).ppf(confidence)
    width, height = 2 * np.sqrt(alpha * eigenvalues)
    return np.mean(x), np.mean(y), width, height, angle


def get_color_list(colors: Colors, levels: int = 1) -> List[Color]:
    """Generate a list of colors.

    colors:
        The source of the color list.
    levels:
        The number of levels in the color list.
    """
    if isinstance(colors, list):
        return colors
    elif isinstance(colors, Colormap):
        cmap = colors
        if len(cmap.colors) != levels:
            cmap = get_cmap(colors.name, lut=levels)
        return list(cmap.colors)
    else:
        try:
            cmap = get_cmap(colors, lut=levels)
            if len(cmap.colors) != levels:
                cmap = get_cmap(cmap.name, lut=levels)
            return list(cmap.colors)
        except ValueError:
            return [colors]

def get_color_map(
        colors: Colors, categories: List[str]) -> Dict[str, Color]:
    """Get a category-color mapping.

    Parameters
    ----------
    colors:
        Color specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        A dictionary mapping category labels to colors.
    """
    color_list = get_color_list(colors, len(categories))
    if not color_list:
        color_list = [None for _ in categories]
    color_map = {}
    for i, category in enumerate(categories):
        color_map[category] = color_list[i % len(color_list)]
    return color_map

def get_font_list(fonts: Fonts) -> List[FontProperties]:
    """Create a list of font properties from a font specification.

    Parameters
    ----------
    fonts:
        The font specification

    Returns
    :
        A list of font properties.
    """
    if isinstance(fonts, FontProperties):
        return [fonts]
    elif isinstance(fonts, str):
        if os.path.exists(fonts):
            return [FontProperties(fname=fonts)]
        return [FontProperties(family=fonts)]
    font_properties = []
    for font in fonts or []:
        font_properties.extend(get_font_list(font))
    return font_properties

def get_font_map(
        fonts: Fonts, categories: List[str]) -> Dict[str, FontProperties]:
    """Get a category-font mapping.

    Parameters
    ----------
    markers:
        Font specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        Mapping between (vowel) categories and fonts.
    """
    font_list = get_font_list(fonts)
    if not font_list:
        font_list = [FontProperties()]
    font_map = {}
    for i, category in enumerate(categories):
        font_map[category] = font_list[i % len(font_list)]
    return font_map

def get_marker_map(
        markers: Markers, categories: List[str]) -> Dict[str, Marker]:
    """Get a category-marker mapping.

    Parameters
    ----------
    markers:
        Marker specification.
    categories:
        A list of (vowel) categories.

    Returns
    -------
    :
        A dictionary mapping category labels to markers.
    """
    if isinstance(markers, list):
        marker_list = markers
    else:
        marker_list = [markers]

    if not marker_list:
        marker_list = [None]

    marker_map = {}
    for i, category in enumerate(categories):
        marker_map[category] = marker_list[i % len(marker_list)]
    return marker_map
