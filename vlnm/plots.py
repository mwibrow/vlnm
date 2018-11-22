"""

This module provides some convenience functions
for producing the more common vowel plots found in the literature.

All the functionality implemented in this module
forms a very thin wrapper around
the |matplotlib| library, and advanced customation of vowel
plots will require familiarity with |matplotlib|.
"""

from typing import Dict, List, Tuple, Union, Type

import matplotlib
from matplotlib.colors import Colormap, ListedColormap
from matplotlib import Path
from matplotlib.font_manager import FontProperties
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats as st


# pylint: disable=C0103
Color = Union[str, tuple]
Colors = Union[List[Color], ListedColormap]
Mark = Union[str, tuple, Path]
Marks = List[Marker]
Font = Union[str, FontProperties]
Fonts = List[Font]

class Columns(dict):
    """Class for creating a vowel context.

    """
    def __init__(
            self,
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            color: Union[str, int] = None,
            marker: Union[str, int] = None,
            label: Union[str, int] = None):
        super().__init__(
            x=x, y=y, color=color, marker=marker, label=label)

    def merge(self, other: Context):
        self.update(
            {key: value for key, value in other.items
             if value is not None})
        return self

class VowelPlot:
    """Class for managing vowel plots.

    """

    def __init__(
            self,
            width: str = None,
            height: str = None,
            rows: str = 1,
            cols: str = 1,
            **kwargs):

        figsize = (width, height) if width and height else None
        self.figure = plt.figure(figsize=figsize)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.cols = rows, cols
        self.kwargs = kwargs

        self.axis = None

    def subplot(self, index: int = None) -> plt.Axes:
        """Get the axis for a subplot."""
        axes = self.figure.get_axes()
        if len(axes) < self.rows * self.cols:
            self.axis = self.figure.add_subplot(
                self.rows, self.cols, len(axes) + 1)
        else:
            self.axis = axes[index]
        return self.axis

    def __enter__(self):
        self.axis = self.subplot()
        return self

    def __exit__(self, *_args):
        pass


    def markers(
            self,
            data: pd.DataFrame = None,
            columns: Dict[str, Union[str, int]],
            color: Color,
            colors: Colors,
            marker: Marker,
            markers: Markers,
            #
            where: str = 'all',
            legend: bool = False,
            **kwargs):
        """Add markers to the vowel plot.

        Parameters
        ----------

        data:
            DataFrame containing the formant data.
        columns:
            A mapping between DataFrame columns and vowel-plot parameters.
        where:
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
            Shorthand for ``colors=[<value>]``
        colors:
            Colors to be used for each vowel category.
            This will be converted into a list of colors
            which will be recycled if there are more vowels
            than colors.
        mark:
            Shorthand for ``marks=[<value>]
        marks:
            Marks to be used for each vowel category.
            This will be converted into a list of marks
            which will be recycled if there are more vowels
            than marks.
        label:
            Shorthand for ``labels=[<value>]``
        labels:
            Label (font) properties to be used for each vowel category.
            This will be converted into a list of properties
            which will be recycled if there are more vowels
            than properties.
        """

        context.merge(dict(
            data=data, x=x, y=y, vowel=vowel, color=color, marker=marker))
        category = (context['vowel'] or context['color'] or context['marker'])
        df = context['data']
        x = context['x']
        y = context['y']
        if which == 'mean':
            df = df.groupby(category, as_index=False).apply(
                lambda group_df: group_df[[x, y]].mean(axis=0))
        elif which == 'median':
            df = df.groupby(category, as_index=False).apply(
                lambda group_df: group_df[[x, y]].median(axis=0))

        categories = sorted(data[category].unique())
        colors = kwargs.pop('colors', context.get('colors'))
        color_map = get_color_map(colors, categories)
        markers = kwargs.pop('markers', context.get('markers'))
        marker_map = get_marker_map(markers, categories)

        grouped = df.groupby(category, as_index=False)
        for category, group_df in grouped:
            pass

    def scatter_(
            self,
            df: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            vowel: str = None,
            vowels: List = None,
            which: str = 'each',
            legend: bool = True,
            colormap: str = 'tab20',
            **kwargs):
        """Add a scatter plot to the vowel plot.

        Paramters
        ---------

        df:
            DataFrame,
        x:
            Column containing the x-axis data.
        y:
            Column containing the y-axis data.
        vowel:
            Column containing the vowel categories/labels.
        vowels:
            List of vowel categories to subset the data.
        which:
            One of ``'each'`` (every row will be plotted)
            or ``'mean'`` (mean formant data per vowel).
        legend:
            Whether to add the vowel categories to the legend.
        colormap:
            Name of a color-map to use for coloring the
            scatter marks.
        """

        df = df or self.kwargs.get('df')
        x = x or self.kwargs.get('x')
        y = y or self.kwargs.get('y')
        vowel = vowel or self.kwargs.get('vowel')

        vowels = vowels or self.kwargs.get('vowels', sorted(df[vowel].unique()))

        if which == 'mean':
            df = df.groupby(vowel, as_index=False).mean()

        try:
            cmap = plt.cm.get_cmap(colormap, len(vowels))
        except TypeError:
            cmap = colormap

        for i, label in enumerate(vowels):
            index = df[vowel] == label
            self.axis.scatter(
                df.loc[index, x], df.loc[index, y],
                c=[cmap(i)],
                label=label,
                **kwargs)
        if legend:
            self.axis.legend()
            self.axis.legend(
                bbox_to_anchor=(1, 1), loc=0, borderaxespad=0., frameon=False)

        if not self.axis.xaxis_inverted():
            self.axis.invert_xaxis()
        if not self.axis.yaxis_inverted():
            self.axis.invert_yaxis()


    def labels(
            self,
            df: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            labels: str = None,
            which: str = 'mean',
            **kwargs):
        """Add labels to the plot.

        Parameters
        ----------
        df:
            Dataframe source of the labels.
        x:
            Column containing x-coordinates.
        y:
            Column containing y-coordinates.
        labels:
            Column containing labels.
        which:
            One of ``'each'`` (every label will be plotted)
            or ``'mean'`` (one label per vowel centered at the formant means).
        **kwargs:
            Other arguments passed on to the `VowelPlot.annotate` method.
        """

        df = df or self.kwargs.get('df')
        x = x or self.kwargs.get('x')
        y = y or self.kwargs.get('y')
        labels = labels or self.kwargs.get('labels')

        if which == 'mean':
            df = df.groupby(labels, as_index=False).mean()
        for key, group_df in df.groupby(labels, as_index=False):
            for xlab, ylab in zip(group_df[x], group_df[y]):
                self.annotate(xlab, ylab, key, **kwargs)

    def annotate(
            self,
            x: float,
            y: float,
            text: str,
            **kwargs):
        """Annotate the axis.

        Parameters
        ----------
        x:
            The x-coordinate.
        y:
            The y-coordinate.
        text:
            The text to add to the plot.
        **kwargs:
            Passes on to `matplotlib.Axis.text`.

        """

        kwargs['horizontalalignment'] = kwargs.get(
            'horizontalalignment', 'center')
        kwargs['verticalalignment'] = kwargs.get(
            'verticalalignment', 'center')
        self.axis.text(x, y, text, **kwargs)

    def axis_labels(self, xlabel: str = None, ylabel: str = None):
        """Set one or more of the axis labels.

        Paramters
        ---------
        xlabel:
            The text for the x-axis label.
        ylabel:
            The text for the y-axis label.
        """
        if xlabel:
            self.axis.set_xlabel(xlabel)
        if ylabel:
            self.axis.set_ylabel(ylabel)

    def legend(self, *args, **kwargs):
        """Set legend options.

        Paramters
        ---------
        *args:
            Passed on to `matplotlib.axes.Axes.legend`.
        *kwargs:
            Passed on to `matplotlib.axes.Axes.legend`.
        """
        self.axis.legend(*args, **kwargs)

    def ellipses(
            self,
            df: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            vowel: str = None,
            include: List[str] = None,
            exclude: List[str] = None,
            color: Union[str, matplotlib.colors.Colormap, list, dict] = None,
            confidence: float = 0.95,
            **kwargs):
        """Add confidence-interval-based ellipsed around formant data.

        Parameters
        ----------
        df:
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
        df = df or self.kwargs.get('df')
        x = x or self.kwargs.get('x', 'f2')
        y = y or self.kwargs.get('y', 'f1')
        vowel = vowel or self.kwargs.get('vowel', 'vowel')
        vowels = df['vowel'].unique()
        if include:
            vowels = [vwl for vwl in vowels if vwl in include]
        if exclude:
            vowels = [vwl for vwl in vowels if not vwl in exclude]
        df = df[df[vowel].isin(vowels)]

        grouped = df.groupby('vowel', as_index=False)
        for _, group_df in grouped:
            width, height, angle = get_confidence_ellipse_params(
                group_df[x], group_df[y], confidence)
            ellipse = mpatches.Ellipse(
                xy=(group_df[x].mean(), group_df[y].mean()),
                width=width,
                height=height,
                angle=angle,
                **kwargs)
            self.axis.add_artist(ellipse)

def get_confidence_ellipse_params(
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
    cov = np.cov(x, y)
    eigenvalues, eignvectors = np.linalg.eig(cov)
    angle = np.arctan2(*np.flip(eignvectors[:, 0])) / np.pi * 180
    alpha = st.chi2(df=2).ppf(confidence)
    width, height = 2 * np.sqrt(alpha * eigenvalues)
    return width, height, angle


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
        if len(colors.colors) != levels:
            cmap = plt.get_cmap(colors.name, lut=levels)
        return cmap.colors
    else:
        try:
            cmap = plt.get_cmap(colors, lut=levels)
            if len(cmap.colors) != levels:
                cmap = plt.get_cmap(cmap.name, lut=levels)
            return cmap.colors
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

    color_map = {}
    for i, category in enumerate(categories):
        color_map[category] = color_list[i % len(color_list)]

    return color_map

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
    marker_map = {}
    for i, category in enumerate(categories):
        marker_map[category] = marker_list[i % len(marker_list)]

    return marker_map



