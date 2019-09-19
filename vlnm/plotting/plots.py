"""
    Plotting module
    ~~~~~~~~~~~~~~~
"""
from collections import OrderedDict
import types
from typing import Dict, Generator, List, Tuple, Union
import uuid

import matplotlib.pyplot as plt
import matplotlib.style as mstyle
from matplotlib.figure import Figure
from matplotlib.axis import Axis
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint

from vlnm.plotting.artists import Artist, EllipseArtist, LabelArtist, MarkerArtist, PolygonArtist
from vlnm.plotting.mappers import get_prop_mapper
from vlnm.plotting.utils import (
    context_from_kwargs,
    create_figure,
    get_confidence_ellipse,
    HandlerEllipse,
    merge,
    merge_contexts,
    strip)

from vlnm.plotting.legends import Legend


def use_style(style):
    """Set the global style for vowel plots."""
    mstyle.use(style)


class VowelPlot:
    """
    Class for managing vowel plots.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, VowelPlot

        df = pb1952()

        plot = VowelPlot(width=5, height=5)
        with plot(data=df, x='f2', y='f1', width=5, height=5):
            plot.markers(color_by='vowel', colors='tab20')
            plot.labels(where='mean')

        ### plot.figure
    """

    def __init__(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            rows: int = 1,
            columns: int = 1,
            width: float = 4,
            height: float = 4,
            figure: Figure = None,
            legend: bool = True,
            **kwargs):

        figsize = kwargs.pop('figsize', (width, height) if width and height else None)
        self.figure = figure or create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.plot_context = strip(dict(data=data, x=x, y=y, invert_axes=True))
        self.axis = None
        self.legends = {}
        self._auto_legend = bool(legend)
        self.legend_options = legend if isinstance(legend, dict) else {}
        self.plot_legend = Legend()

    def __getattr__(self, attr):
        if self.axis and hasattr(self.axis, attr):
            return getattr(self.axis, attr)
        if hasattr(plt, attr):
            return getattr(plt, attr)
        return object.__getattribute__(self, attr)

    def __enter__(self):
        return self.start_plot()

    def __exit__(self, exc_type, _exc_value, _traceback):
        if exc_type:
            return False
        return self.end_plot()

    def __call__(self, **kwargs):
        return self.context(**kwargs)

    def context(self, **kwargs):
        self.plot_context = merge(self.plot_context, kwargs)
        return self

    def start_plot(self):
        return self

    def end_plot(self):
        # if self._auto_legend:
        #     legend_ids = list(self.legends.keys())
        # for legend_id in legend_ids:
        #     self.legend(legend_id)
        if self.axis:
            if not self.get_xlabel():
                self.xlabel(self.plot_context['x'])
            if not self.get_ylabel():
                self.ylabel(self.plot_context['y'])
        return self.figure

    def subplot(
            self,
            row: int = None,
            column: int = None,
            label: str = None,
            invert_axes: str = None,
            **kwargs) -> Axis:
        if not column:
            index = row - 1
            row = (index // self.rows) + 1
            column = (index % self.columns) + 1
        label = label or '{}-{}'.format(row, column)
        index = (row - 1) * self.columns + column
        self.axis = self.figure.add_subplot(
            self.rows, self.columns, index, label=label, **kwargs)
        if invert_axes or self.plot_context.get('invert_axes'):
            if not self.axis.xaxis_inverted():
                self.axis.invert_xaxis()
            if not self.axis.yaxis_inverted():
                self.axis.invert_yaxis()
        return self.axis

    @staticmethod
    def _aggregate_df(df, columns, groups=None, where=None):
        if where:
            if where == 'mean':
                df = df.groupby(groups, as_index=True).apply(
                    lambda group_df: group_df[columns].mean(axis=0))
                df = df.reset_index()
            elif where == 'median':
                df = df.groupby(groups, as_index=True).apply(
                    lambda group_df: group_df[columns].median(axis=0))
                df = df.reset_index()
        return df

    def _df_iterator(
            self, context: Dict) -> Generator[Tuple[Axis, pd.DataFrame, Dict, Dict], None, None]:

        df = context['data']
        x = context['x']
        y = context['y']
        where = context.get('where')
        groups = []
        prop_mappers = {}
        plot_mapper = {}

        # Aggregate df if required.
        groups = list(set(value for key, value in context.items() if key.endswith('_by')))
        if where:
            df = self._aggregate_df(df, [x, y], groups, where)

        # Get property mappers.
        for key, value in context.items():
            if key.endswith('_by'):
                prop = key[:-3]
                group = value
                mapping = context.get(prop)
                if prop:
                    if prop == 'plot':  # plot mapping is special
                        plot_mapper[group] = get_prop_mapper(
                            prop, mapping=mapping, data=df[group])
                    elif prop in ['group', 'label']:  # special cases
                        pass
                    else:
                        prop_mappers[group] = prop_mappers.get(group, [])
                        prop_mappers[group].append(
                            get_prop_mapper(prop, mapping=mapping, data=df[group]))

        if groups:
            # Iterate over groups.
            grouped = df.groupby(groups, as_index=False)
            params = context.get('defaults', {}).copy()
            for values, group_df in grouped:
                values = values if isinstance(values, tuple) else (values,)
                props = params.copy()
                group_props = {}
                plot_props = {}
                group_values = {}

                for group, value in zip(groups, values):
                    group_values[group] = value
                    if group in prop_mappers:
                        mapped_props = {}
                        for prop_mapper in prop_mappers[group]:
                            mapped_props.update(prop_mapper.get_props(value))
                        mapped_props.update(**context.get('_params', {}))
                        group_props[group] = group_props.get(group, OrderedDict())
                        group_props[group][value] = merge(params, mapped_props)
                        props.update(**mapped_props)
                    else:
                        props.update(**context.get('_params', {}))
                    if group in plot_mapper:
                        plot_props = plot_mapper[group].get_props(value)

                if plot_props:
                    axis = self.subplot(**plot_props)
                else:
                    axis = self.axis or self.subplot(row=1, column=1)

                yield axis, group_df, props, group_props

    def _update_legend(
            self,
            legend_id: str,
            group_props: dict,
            artist: Artist,
            legend_options: dict):

        for group in group_props:
            for label in group_props[group]:
                self.plot_legend.add_entry(
                    legend_id, group, label, artist(**group_props[group][label]))
            self.plot_legend.update_options(legend_id=legend_id, **legend_options)

        # legend, _ = self.legends.get(legend_id, ({}, {}))
        # for group in group_props:
        #     legend[group] = legend.get(group, OrderedDict())
        #     for label in group_props[group]:
        #         legend[group][label] = artist(**group_props[group][label])
        # self.legends[legend_id] = (legend, legend_options or self.legend_options)

    def legend(self, legend_id=None, **kwargs):
        """Add a legend to the current axis.
        """
        legend_ids = list(self.legends.keys())

        if not legend_ids:
            return
        legend_id = legend_id or legend_ids[0]
        legend, legend_options = self.legends[legend_id]

        if 'handler_map' not in kwargs:
            kwargs['handler_map'] = {
                mpatches.Ellipse: HandlerEllipse()
            }

        legend_options.update(**kwargs)
        title = legend_options.pop('title', [])
        if isinstance(title, str):
            title = [title]

        for i, group in enumerate(legend):
            handles = list(legend[group].values())
            labels = list(legend[group].keys())
            legend_artist = plt.legend(
                handles=handles,
                labels=labels,
                title=title[i] if title else group,
                **legend_options)
            self.axis.add_artist(legend_artist)

    @staticmethod
    def _generate_legend_id(prefix):
        return '{}-{}'.format(prefix, uuid.uuid1())

    def markers(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            where: str = 'all',
            legend: Union[str, dict] = None,
            **kwargs) -> 'VowelPlot':

        context, params = context_from_kwargs(kwargs)

        context = merge_contexts(
            self.plot_context,
            context,
            dict(data=data, x=x, y=y, where=where, _params=params))

        artist = MarkerArtist()

        legend_id = legend if isinstance(legend, str) else self._generate_legend_id('markers')

        for axis, group_df, props, group_props in self._df_iterator(context):
            x = group_df[context['x']]
            y = group_df[context['y']]
            artist.plot(axis, x, y, **props)
            if legend:
                self._handle_legend_entry(legend_id, legend, group_props, artist.legend)

        return self

    def _handle_legend_entry(self, legend_id, legend, artist_props, artist):
        if legend == False:
            return
        legend_options = {}
        if isinstance(legend, dict):
            legend_options = legend
        self._update_legend(legend_id, artist_props, artist, legend_options)

    def labels(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            where: str = 'all',
            label_by: str = None,
            label: Union[str, dict, list, types.FunctionType] = None,
            legend: str = None, **kwargs) -> 'VowelPlot':

        context, params = context_from_kwargs(kwargs)

        context = merge_contexts(
            self.plot_context,
            context,
            dict(data=data, x=x, y=y, where=where, label_by=label_by, _params=params))
        artist = LabelArtist()

        for axis, group_df, props, group_props in self._df_iterator(context):
            x = group_df[context['x']]
            y = group_df[context['y']]
            labels = group_df[context['label_by']]
            artist.plot(axis, x, y, labels, **props)

        return self

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
            **kwargs) -> 'VowelPlot':
        """
        Add a polygon to the
        """
        context, params = context_from_kwargs(kwargs)

        context = merge_contexts(
            self.plot_context,
            context,
            dict(data=data, x=x, y=y, where=where, _params=params))

        if legend_only:
            legend = legend_only

        artist = PolygonArtist()

        legend_id = legend if isinstance(legend, str) else self._generate_legend_id('polygon')

        x = context['x']
        y = context['y']

        for axis, group_df, props, group_props in self._df_iterator(context):
            xy = []
            if hull:
                group_x = group_df[x].groupby(vertex).apply(np.mean)
                group_y = group_df[y].groupby(vertex).apply(np.mean)
                convex_hull = MultiPoint(
                    map(tuple, zip(group_x, group_y))).convex_hull
                xy.extend([(x, y) for x, y in convex_hull.coords])
            else:
                for vert in enumerate(vertices):
                    i = group_df[vertex] == vert
                    group_x = group_df[i, x].mean()
                    group_y = group_df[i, y].mean()
                    xy.append((group_x, group_y))

            artist.plot(axis, xy, closed=closed, **props)

            axis.relim()
            axis.autoscale_view()

            if legend:
                self._handle_legend_entry(legend_id, legend, group_props, artist.legend)
            return self

    def polyline(
            self,
            vertex: Union[str, int],
            vertices: List[str],
            where: Union[str, types.FunctionType],
            hull=True,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            legend: Union[str, bool] = False,
            legend_only: Union[str, bool] = False,
            **kwargs):
        """Add lines to the plot.

        This is just a wrapper around :method:`VowelPlot.polygon`
        with ``closed=False``.

        """
        return self.polygon(
            vertex=vertex, vertices=vertices, where=where, hull=hull, data=data,
            x=x, y=y, legend=legend, lenged_only=legend_only, closed=False, **kwargs)

    def ellipses(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            confidence: float = 0.95,
            n_std: float = None,
            n_mad: float = None,
            legend: str = '',
            ** kwargs):
        """Add confidence-interval-based ellipses around formant data.


        """
        context, params = context_from_kwargs(kwargs)

        context = merge_contexts(
            self.plot_context,
            context,
            dict(data=data, x=x, y=y, _params=params))

        artist = EllipseArtist()

        x = context['x']
        y = context['y']

        legend_id = legend if isinstance(legend, str) else self._generate_legend_id('ellipses')
        for axis, group_df, props, group_props in self._df_iterator(context):
            group_x = group_df[x]
            group_y = group_df[y]
            center_x, center_y, width, height, angle = get_confidence_ellipse(
                group_x, group_y, confidence=confidence, n_std=n_std, n_mad=n_mad)
            artist.plot(axis, (center_x, center_y), width, height, angle, **props)
            axis.relim()
            axis.autoscale_view()
            if legend:
                self._handle_legend_entry(legend_id, legend, group_props, artist.legend)
        return self
