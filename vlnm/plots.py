"""
This module provides some convenience functions
for producing the more common vowel plots found in the literature.

All the functionality implemented in this module
forms a very thin wrapper around
the |matplotlib| library, and advanced customation of vowel
plots will require familiarity with |matplotlib|.
"""

from collections import OrderedDict
from typing import Dict, List, Tuple, Union
import types

from matplotlib.axes import Axes
from matplotlib.cm import get_cmap
from matplotlib.figure import Figure
from matplotlib.legend_handler import HandlerPatch
from matplotlib.lines import Line2D
from matplotlib.path import Path
import matplotlib.colors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint
import scipy.stats as st


def create_figure(*args, **kwargs):
    return plt.figure(*args, **kwargs)

def merge_dicts(*dicts):
    if not dicts:
        return {}
    merged = {}
    for dct in dicts:
        merged.update({
            key: value for key, value in dct.items()
            if value is not None})
    return merged

__VOWEL_PLOT__ = None

def get_plot():
    """Get the current plot instance."""
    global __VOWEL_PLOT__  # pylint: disable=global-statement
    return __VOWEL_PLOT__

def set_plot(plot):
    """Set the current plot."""
    global __VOWEL_PLOT__  # pylint: disable=global-statement
    __VOWEL_PLOT__ = plot

class VowelPlot(object):
    """Class for managing vowel plots.
    """

    def __init__(
            self,
            width: float = 4,
            height: float = 4,
            rows: int = 1,
            columns: int = 1,
            figure: Figure = None,
            context: dict = None,
            **kwargs):

        figsize = (width, height) if width and height else None
        self.figure = figure or create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.plot_context = context or {}
        self.axis = None
        self.legends = {}

        set_plot(self)

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
            relabel: Dict[str, str] = None,
            #
            where: str = 'all',
            legend: str = '',
            legend_only: bool = False,
            **kwargs):
        """Add markers to the vowel plot.

        """
        if legend_only:
            legend = legend_only

        context, kwargs = get_context_kwargs(
            kwargs, keys=['axis', 'legend_artist'])
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data, x=x, y=y,
                where=where, relabel=relabel,
                kwargs=kwargs,
                defaults=dict(
                    marker='.',
                    edgecolor='none',
                    facecolor='black'
                )
            ),
            context)

        iterator = self._group_iterator(context)

        mpl_props = {
            'color': ['edgecolor', 'facecolor'],
            'edgecolor': 'markeredgecolor',
            'facecolor': 'markerfacecolor',
            'size': 'markersize',
            'linewidth': 'markeredgewidth'
        }
        for axis, group_df, props, group_props in iterator:
            group_x = group_df[context['x']]
            group_y = group_df[context['y']]


            props = translate_props(props, mpl_props)

            props.update(linestyle='', drawstyle=None)
            axis.plot(group_x, group_y, **props)

            if legend:
                def _artist(**props):
                    props = translate_props(props, mpl_props)
                    return Line2D(
                        [0], [0], linestyle='', drawstyle=None, **props)

                self._update_legend(legend, group_props, _artist)


    def _update_legend(self, legend_id, group_props, artist):
        legend = self.legends.get(legend_id, {})
        for group in group_props:
            legend[group] = legend.get(group, OrderedDict())
            for label in group_props[group]:
                legend[group][label] = artist(**group_props[group][label])
        self.legends[legend_id] = legend

    def legend(self, legend_id=None, **kwargs):
        """Add a legend to the current axis.
        """
        legend_ids = list(self.legends.keys())
        legend_id = legend_id or legend_ids[0]
        legend = self.legends[legend_id]

        if 'handler_map' not in kwargs:
            kwargs['handler_map'] = {
                mpatches.Ellipse: _HandlerEllipse()
            }

        for group in legend:
            handles = list(legend[group].values())
            labels = list(legend[group].keys())
            legend_artist = plt.legend(
                handles=handles,
                labels=labels,
                title=group,
                **kwargs)
            self.axis.add_artist(legend_artist)

    def labels(
            self,
            data: pd.DataFrame = None,
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            relabel: Dict[str, str] = None,
            #
            where: str = 'all',
            **kwargs):
        """Add labels to the vowel plot.

        """

        context, kwargs = get_context_kwargs(kwargs, keys=None)
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data, x=x, y=y,
                where=where, relabel=relabel,
                kwargs=kwargs,
                defaults=dict(
                    color='black',
                    horizontalalignment='center',
                    verticalalignment='center',
                )
            ),
            context)

        if 'label' not in context:
            context['label'] = list(
                context['data'][context['label_by']].unique())

        relabel = context.get('relabel') or {}

        iterator = self._group_iterator(context)

        min_x = min_y = np.inf
        max_x = max_y = -np.inf
        for axis, group_df, props in iterator:
            group_x = group_df[context['x']]
            group_y = group_df[context['y']]
            props = translate_props(
                props,
                {
                    'size': 'fontsize',
                    'label': 'text'
                })

            props['text'] = relabel.get(props['text'], props['text'])
            for text_x, text_y in zip(group_x, group_y):
                text = mtext.Text(x=text_x, y=text_y, **props)
                axis.add_artist(text)

            # Text artist does not update the bounding box :(
            min_x = np.min([min_x, group_x])
            min_y = np.min([min_y, group_y])
            max_x = np.max([max_x, group_x])
            max_y = np.max([max_y, group_y])


            # Update the axis.
            rect = mpatches.Rectangle(
                (min_x, min_y),
                width=max_x - min_x,
                height=max_y - min_y,
                angle=0,
                fill=False,
                facecolor='none',
                edgecolor='none')
            axis.add_patch(rect)
            axis.relim()
            axis.autoscale_view()


    def polygon(
            self,
            vertex: Union[str, int],
            vertices: List[str],
            where: Union[str, types.FunctionType],
            closed: bool = True,
            hull=True,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            legend: Union[str, bool] = False,
            legend_only: Union[str, bool] = False,
            **kwargs):

        context, kwargs = get_context_kwargs(kwargs, keys=None)
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data, x=x, y=y,
                where=where,
                kwargs=kwargs,
                defaults=dict(
                    color='black',
                    line='-',
                    closed=closed
                )
            ),
            context)

        if legend_only:
            legend = legend_only

        iterator = self._group_iterator(context)

        mpl_props = {
            'color': ['edgecolor', 'facecolor'],
            'line': 'linestyle'
        }
        for axis, group_df, props, group_props in iterator:

            props = translate_props(props, mpl_props)

            xy = []
            if hull:
                group_x = group_df[context['x']].groupby(vertex).apply(np.mean)
                group_y = group_df[context['y']].groupby(vertex).apply(np.mean)
                convex_hull = MultiPoint(
                    map(tuple, zip(group_x, group_y))).convex_hull
                xy.extend([(x, y) for x, y in convex_hull.vertices])
            else:
                for vert in enumerate(vertices):
                    i = group_df[vertex] == vert
                    group_x = group_df[i, context['x']].mean()
                    group_y = group_df[i, context['y']].mean()
                    xy.append((group_x, group_y))

            polygon = mpatches.Polygon(
                xy=xy,
                **props)
            axis.add_patch(polygon)

            axis.relim()
            axis.autoscale_view()

            if legend:
                def _artist(**props):
                    props = translate_props(props, mpl_props)
                    return mpatches.Polygon(
                        xy=[(0.25, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0)],
                        **props)

                self._update_legend(legend, group_props, _artist)

    def ellipses(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            confidence: float = 0.95,
            legend: str = '',
            **kwargs):
        """Add confidence-interval-based ellipsed around formant data.

        """
        context, kwargs = get_context_kwargs(kwargs, keys=None)
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data, x=x, y=y,
                kwargs=kwargs,
                defaults=dict(
                    facecolor='none',
                    edgecolor='black',
                    linestyle='-',
                )
            ),
            context)

        iterator = self._group_iterator(context)

        mpl_props = {
            'color': ['edgecolor', 'facecolor'],
            'line': 'linestyle'
        }
        for axis, group_df, props, group_props in iterator:

            props = translate_props(props, mpl_props)

            group_x = group_df[context['x']]
            group_y = group_df[context['y']]
            center_x, center_y, width, height, angle = get_confidence_ellipse(
                group_x, group_y, confidence)

            ellipse = mpatches.Ellipse(
                xy=(center_x, center_y),
                width=width,
                height=height,
                angle=angle,
                **props)
            axis.add_patch(ellipse)
            axis.relim()
            axis.autoscale_view()

            if legend:
                def _artist(**props):
                    props = translate_props(props, mpl_props)
                    return mpatches.Ellipse(
                        xy=(0.5, 0.5),
                        width=1,
                        height=0.625,
                        angle=0,
                        **props)

                self._update_legend(legend, group_props, _artist)


    def arrows(
            self,
            arrowstyle: str = '->',
            data: pd.DataFrame = None,
            x: List[str] = None,
            y: List[str] = None,
            legend: Union[str, bool] = False,
            legend_only: Union[str, bool] = False,
            where=None,
            **kwargs):

        context, kwargs = get_context_kwargs(kwargs, keys=None)
        context = merge_dicts(
            self.plot_context,
            dict(
                data=data,
                x=x,
                y=y,
                where=where,
                kwargs=kwargs,
                defaults=dict(
                    color='black',
                    linestyle='-',
                )
            ),
            context)

        if legend_only:
            legend = legend_only

        iterator = self._group_iterator(context)

        mpl_props = dict()

        for axis, group_df, props, group_props in iterator:

            props = translate_props(props, mpl_props)
            size = props.pop('size', 1) * 2
            for _, row in group_df.iterrows():
                vertices = list(map(tuple, zip(
                    row[context['x']], row[context['y']])))
                if len(vertices) < 2:
                    raise ValueError('Not enough points to draw arrows')
                codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1)
                arrow = mpatches.FancyArrowPatch(
                    posA=None,
                    posB=None,
                    path=Path(vertices, codes),
                    arrowstyle=arrowstyle,
                    shrinkA=0, shrinkB=0,
                    mutation_scale=size,
                    **props)

                axis.add_patch(arrow)

            axis.relim()
            axis.autoscale_view()

            if legend:
                def _artist(**props):
                    props = translate_props(props, mpl_props)
                    size = props.pop('size', 0) * 2
                    return mpatches.FancyArrowPatch(
                        posA=None,
                        posB=None,
                        path=Path(
                            [(0, 0), (1, 1)],
                            [Path.MOVETO, Path.LINETO]),
                        arrowstyle=arrowstyle,
                        connectionstyle=None,
                        shrinkA=0, shrinkB=0,
                        mutation_scale=size,
                        **props)

                self._update_legend(legend, group_props, _artist)

    def __getattr__(self, attr):
        if hasattr(self.axis, attr):
            return getattr(self.axis, attr)
        if hasattr(plt, attr):
            return getattr(plt, attr)
        return object.__getattribute__(self, attr)


    def _group_iterator(self, context):
        df = context['data']

        props_by = {}
        prop_mappers = {}
        groups = []
        index_mappings = {}

        for key, group in context.items():
            if key.endswith('_by'):
                prop = key[:-3]
                props_by[group] = props_by.get(group, []) + [prop]
                prop_mappers[prop] = self._get_prop_mapper(prop, context.get(prop))
                if group not in groups:
                    groups.append(group)
                    index_mappings[group] = {}
                    for i, unique in enumerate(df[group].unique()):
                        index_mappings[group][unique] = i

        df = _aggregate_df(
            df,
            groups=groups,
            columns=[context.get('x'), context.get('y')],
            where=context.get('where'))

        df_iteration = df_iterator(df, groups)
        for value_map, group_df in df_iteration:

            props = context.get('defaults', {}).copy()
            group_props = {}
            for group in groups:
                value = value_map[group]
                index = index_mappings[group][value]
                group_props[group] = group_props.get(value, {})
                group_props[group][value] = context.get('defaults', {}).copy()
                for prop in props_by[group]:
                    mapper = prop_mappers[prop]
                    index = index_mappings[group][value]
                    mapped_props = get_mapped_props(prop, mapper, value, index)
                    group_props[group][value].update(**mapped_props)
                    props.update(**mapped_props)
                group_props[group][value].update(**context.get('kwargs', {}))

            axis = props.pop('axis', self.axis)
            props.update(**context.get('kwargs', {}))
            yield axis, group_df, props, group_props

    def _get_prop_mapper(self, prop, values):
        if prop == 'plot':
            def _mapper(_, index):
                return dict(axis=self.subplot(index=index))
            return _mapper
        if 'color' in prop:
            return get_color_cycle(values)
        if isinstance(values, (dict, list, types.FunctionType)):
            return values
        return [values]

def _aggregate_df(df, groups=None, columns=None, where=None):
    if groups and columns and where:
        if where == 'mean':
            df = df.groupby(groups, as_index=True).apply(
                lambda group_df: group_df[columns].mean(axis=0))
            df = df.reset_index()
        elif where == 'median':
            df = df.groupby(groups, as_index=True).apply(
                lambda group_df: group_df[columns].median(axis=0))
            df = df.reset_index()
    return df

class _HandlerEllipse(HandlerPatch):
    def create_artists(
            self, legend, orig_handle,
            xdescent, ydescent, width, height, fontsize, transform):
        center = (width - xdescent) / 2, (height - ydescent) / 2
        patch = mpatches.Ellipse(
            xy=center, width=(width + xdescent),
            height=height + ydescent)
        self.update_prop(patch, orig_handle, legend)
        patch.set_transform(transform)
        return [patch]


def get_mapped_props(prop, mapper, value, index):
    try:
        mapped_value = mapper(value, index)
    except TypeError:
        try:
            mapped_value = mapper[value]
        except TypeError:
            mapped_value = mapper[index % len(mapper)]
    if isinstance(mapped_value, dict):
        return mapped_value
    return {prop: mapped_value}

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
        for values, group_df in df.groupby(groups, as_index=False):
            if not isinstance(values, tuple):
                values = (values,)
            value_map = {group: value for group, value in zip(groups, values)}
            yield value_map, group_df
    else:
        yield {}, df

def make_legend_entries(legend, specs, defaults):
    entries = {}
    for spec in specs:
        group = spec['group']
        label = spec['label']
        props = spec['props']
        artist = spec['artist']

        if group in legend and label in legend[group]:
            continue
        if group in entries:
            entries[group][label]['props'].update(props)
        else:
            entries[group] = OrderedDict()
            entries[group][label] = dict(props=defaults, artist=artist)
            entries[group][label]['props'].update(**props)

    for group in entries:
        for label in entries[group]:
            props = entries[group][label].pop('props')
            artist = entries[group][label].pop('artist')
            entries[group][label] = artist(**props)
    return entries

def get_context_kwargs(kwargs, keys=None):
    context = {}
    keys = set(keys or [])
    for key, value in kwargs.items():
        if key in keys:
            context[keys] = value
        elif key.endswith('_by'):
            context[key] = value
            prop = key[:-3]
            context[prop] = kwargs.get(prop)
    rest = {key: value for key, value in kwargs.items() if key not in context}
    return context, rest

def translate_props(props, prop_translator):
    renamed_props = {}
    for prop, value in props.items():
        if prop in prop_translator:
            names = prop_translator[prop]
            if names is None:
                continue
            names = names if isinstance(names, list) else [names]
            for name in names:
                renamed_props.update(
                    **translate_props({name: value}, prop_translator))
        else:
            renamed_props[prop] = value
    return renamed_props

def get_color_cycle(colors):
    """Generate a color cycle.
    """
    if isinstance(colors, (list, dict)):
        return colors
    elif isinstance(colors, matplotlib.colors.Colormap):
        return list(colors.colors)
    else:
        try:
            return list(get_cmap(colors).colors)
        except ValueError:
            return [colors]
