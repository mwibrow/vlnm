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
            vowel: Union[str, int] = 'vowel',
            style: Union[str, Dict[str, any]] = None,
            vary: Dict[str, str] = None,
            relabel: Dict[str, str] = None,
            replace=False):
        """Set or update the context for the current plot.

        plot(data=df, x='f2', y='f1', vowel='vowel'
            style=by(color='tab20', marker='.'),
            vary=by(color='vowel))
        """
        plot_context = dict(
            data=data, x=x, y=y, vowel=vowel, style=style, vary=vary,
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
            vowel: Union[str, int] = None,
            style: Union[str, Dict[str, str]] = None,
            vary: Dict[str, any] = None,
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
                style=style,
                vary=vary,
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

            # if legend:
            #     kwargs['label'] = key

            self.axis.scatter(
                group_x, group_y, s=size, c=[color], marker=marker, **kwargs)

        # if legend:
        #     self.axis.legend()


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

    x = context.get('x')
    y = context.get('y')
    vary = context.get('vary') or {}
    style = context.get('style') or {}
    where = context.get('where')

    vary_columns = list(vary.values())
    groups = context.get('groups', []) or []
    for column in vary_columns:
        if not column in groups:
            groups.append(column)

    style_maps = dict()
    for prop, column in vary.items():
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
        style_map = get_group_styles(groups, values, vary, style_maps)
        yield group_df[x], group_df[y], column_map, style_map
