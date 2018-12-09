"""

This module provides some convenience functions
for producing the more common vowel plots found in the literature.

All the functionality implemented in this module
forms a very thin wrapper around
the |matplotlib| library, and advanced customation of vowel
plots will require familiarity with |matplotlib|.
"""

from typing import Dict, List, Tuple, Union

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib import Path
from matplotlib.font_manager import FontProperties
import matplotlib.patches as mpatches
import matplotlib.pyplot as PYPLOT
import pandas as pd
import numpy as np
import scipy.stats as st

from vlnm.plotting.style import (
    Color, Colors,
    Line, Lines,
    Marker, Markers,
    get_color_map,
    get_marker_map,
    get_line_map,
    get_group_styles)

# pylint: disable=C0103
Style = Union[str, Dict[str, any]]
Vary = Dict[str, str]

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
    return PYPLOT.figure(*args, **kwargs)

def by(**kwargs):
    """Syntactic sugar function for creating dictionarys."""
    return dict(**kwargs)

def merge_dicts(*dicts):
    if not dicts:
        return {}
    merged = {}
    for dct in dicts:
        merged.update({
            key: value for key, value in dct.items()
            if value is not None})
    return merged

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
    relabel:
        A dictionary which maps vowel categories/labels onto
        alternative strings.
    color:
        Colors to be used for each vowel category.
        This will be converted into a list of colors
        where will be recycled if there are more vowels
        than colors.
    marker:
        Marks to be used for each vowel category.
        This will be converted into a list of marks
        where will be recycled if there are more vowels
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
            width: str = 4,
            height: str = 4,
            rows: str = 1,
            columns: str = 1,
            figure: Figure = None,
            context: dict = None,
            **kwargs):

        figsize = (width, height) if width and height else None
        self.figure = figure or _create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.plot_context = context or {}
        self.axis = None

    def __call__(self, **kwargs):
        return self.set_context(**kwargs)

    def context(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = 'f2',
            y: Union[str, int] = 'f1',
            relabel: Dict[str, str] = None,
            replace=False):
        """Set or update the context for the current plot.


        """
        plot_context = dict(
            data=data, x=x, y=y,
            relabel=relabel)
        if replace:
            self.plot_context = plot_context
        else:
            self.plot_context.update(plot_context)
        return self


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
            color: Colors = None,
            color_by: str = None,
            marker: Markers = None,
            marker_by: str = None,
            relabel: Dict[str, str] = None,
            #
            where: str = 'all',
            legend: bool = False,
            size: float = None,
            groups: List[str] = None,
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
        style:
            Plot style to use.
        relabel:
            A dictionary which maps vowel categories/labels onto
            alternative strings.
        size:
            Size of markers.
        groups:
        """

        context = merge_dicts(
            self.plot_context,
            dict(
                data=data,
                x=x, y=y,
                color_by=color_by,
                color=color,
                marker_by=marker_by,
                marker=marker,
                relabel=relabel))

        iterator = plot_iterator(context['data'], groups, context)
        for group_x, group_y, _, style_map in iterator:
            color = style_map.get('color')
            if color is None:
                color = 'black'
            marker = style_map.get('marker') or '.'

            kwargs.pop('c', None)
            kwargs.pop('cmap', None)
            kwargs.pop('s', None)

            self.axis.scatter(
                group_x, group_y, s=size, c=[color], marker=marker, **kwargs)

    def labels(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            color: Colors = None,
            color_by: str = None,
            label: Markers = None,
            label_by: str = None,
            relabel: Dict[str, str] = None,
            #
            where: str = 'all',
            legend: bool = False,
            size: float = None,
            groups: List[str] = None,
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
        style:
            Plot style to use.
        relabel:
            A dictionary which maps vowel categories/labels onto
            alternative strings.
        size:
            Size of markers.
        groups:
        """

        context = merge_dicts(
            self.plot_context,
            dict(
                data=data,
                x=x, y=y,
                color_by=color_by,
                color=color,
                label_by=label_by,
                where=where,
                relabel=relabel))

        relabel = context.get('relabel') or {}
        iterator = plot_iterator(context['data'], groups, context)
        for group_x, group_y, value_map, style_map in iterator:
            color = style_map.get('color')
            if color is None:
                color = 'black'

            label_by = context.get('label_by')
            label = value_map[label_by]
            if label in relabel:
                label = relabel[label]

            kwargs['horizontalalignment'] = kwargs.get(
                'horizontalalignment', 'center')
            kwargs['verticalalignment'] = kwargs.get(
                'verticalalalignment', 'center')
            size = size or kwargs['fontsize']
            kwargs['fontsize'] = size

            for text_x, text_y in zip(group_x, group_y):
                self.axis.text(text_x, text_y, label, color=color, **kwargs)

    def ellipses(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            color: Colors = None,
            color_by: str = None,
            line: Lines = None,
            line_by: str = None,
            confidence: float = 0.95,
            groups: List[str] = None,
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
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data,
                x=x, y=y,
                color_by=color_by,
                color=color,
                line=line,
                line_by=line_by))

        iterator = plot_iterator(context['data'], groups, context)
        for group_x, group_y, _, style_map in iterator:
            center_x, center_y, width, height, angle = get_confidence_ellipse(
                group_x, group_y, confidence)

            color = style_map.get('color')
            if color is None:
                color = 'black'
            line = style_map.get('line')

            ellipse = mpatches.Ellipse(
                xy=(center_x, center_y),
                width=width,
                height=height,
                angle=angle,
                color=color,
                linestyle=line,
                **kwargs)
            self.axis.add_artist(ellipse)

    def __getattr__(self, attr):
        if hasattr(self.axis, attr):
            return getattr(self.axis, attr)
        if hasattr(PYPLOT, attr):
            return getattr(PYPLOT, attr)
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


def df_iterator(df, groups):
    """Helper function for iterating over DataFrame groups."""
    if groups:
        for group, group_df in df.groupby(groups, as_index=False):
            if not isinstance(group, tuple):
                group = (group,)
            yield group, group_df
    else:
        yield (), df

def plot_iterator(df, groups, context):
    """Helper function to iterate over data groups."""
    x = context.get('x')
    y = context.get('y')
    vary_by = {}
    style = {}

    for key in context:
        if key.endswith('_by'):
            prop = key[:-3]
            vary_by[prop] = context[key]
            if prop in context:
                style[prop] = context[prop]

    where = context.get('where')

    vary_columns = list(vary_by.values())
    groups = context.get('groups', []) or []
    for column in vary_columns:
        if not column in groups:
            groups.append(column)

    style_maps = dict()
    for prop, column in vary_by.items():
        if prop == 'color':
            categories = list(df[column].unique())
            style_maps[prop] = get_color_map(style.get(prop), categories)

    if where == 'mean':
        df = df.groupby(groups, as_index=True).apply(
            lambda group_df: group_df[[x, y]].mean(axis=0))
        df = df.reset_index()
    elif where == 'median':
        df = df.groupby(groups, as_index=True).apply(
            lambda group_df: group_df[[x, y]].median(axis=0))
        df = df.reset_index()

    for values, group_df in df_iterator(df, groups):
        column_map = {
            column: value for column, value in zip(groups, values)}
        style_map = get_group_styles(groups, values, vary_by, style_maps)
        yield group_df[x], group_df[y], column_map, style_map
