"""
    Plotting module
    ~~~~~~~~~~~~~~~
"""

import types
from typing import Dict, Generator, List, Tuple, Union
import uuid

import matplotlib.pyplot as plt
import matplotlib.style as mstyle
from matplotlib.figure import Figure
from matplotlib.axis import Axis
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint
import scipy.stats as st

from vlnm.plotting.artists import (
    Artist, ContourArtist, EllipseArtist, LabelArtist, LineArtist, MarkerArtist, PolygonArtist)
from vlnm.plotting.mappers import (
    GroupPropsMapper
)
from vlnm.plotting.utils import (
    aggregate_df,
    create_figure,
    get_confidence_ellipse)

from vlnm.plotting.bounds import BoundingBox

from vlnm.plotting.legends import Legend

from vlnm.plotting.settings import Settings
from vlnm.plotting.arrows import FancierArrow


def use_style(style):
    """Set the global style for vowel plots."""
    mstyle.use(style)


def split_context(**kwargs):
    prop_groups, prop_values, params = {}, {}, {}
    for key, value in kwargs.items():
        if key.endswith('_by'):
            prop_groups[key[:-3]] = value
        elif key + '_by' in kwargs:
            prop_values[key] = value
        else:
            params[key] = value
    return prop_groups, prop_values, params


def generate_legend_id(prefix):
    return '{}-{}'.format(prefix, uuid.uuid1())


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


    """

    def __init__(
            self,
            data: pd.DataFrame = None,
            x: str = 'f2',
            y: str = 'f1',
            rows: int = 1,
            columns: int = 1,
            width: float = 4,
            height: float = 4,
            figure: Figure = None,
            axes: Union[list, dict] = None,
            **kwargs):

        figsize = kwargs.pop('figsize', (width, height) if width and height else None)
        self.figure = figure or create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.axes = None
        self.axis = None
        if figure:
            self.axes = axes or figure.get_axes()

        self.legends = Legend()

        self.settings = Settings(
            axis=dict(invert_axes=True),
            data=dict(data=data, x=x, y=y),
            legend=dict(
                frameon=False,
            ),
            markers={},
            labels={}
        )

    def __getattr__(self, attr):  # pragma: no cover
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

    def groups_iterator(
            self,
            data: dict,
            context: dict) -> Generator[Tuple[Axis, pd.DataFrame, Dict, Dict], None, None]:

        df, x, y, where = data['data'], data['x'], data['y'], data.get('where')

        prop_groups, prop_values, params = split_context(**context)

        groups = list(set(prop_groups.values()))
        # hoist axis group
        if 'axis' in groups:
            groups.remove('axis')
            groups = ['axis'] + groups

        if where:
            df = aggregate_df(df, [x, y], groups, where)

        group_props_mapper = GroupPropsMapper(groups)
        for prop, group in prop_groups.items():
            group_props_mapper.add_prop_mapper(group, prop, prop_values[prop])

        if groups:
            # Iterate over groups.
            grouped = df.groupby(groups, as_index=False)

            for values, group_df in grouped:
                if group_df.empty:
                    continue
                values = values if isinstance(values, tuple) else (values,)

                props = {}
                group_props = group_props_mapper.get_props(groups, values, plot=self)
                for grp_props in group_props.values():
                    props.update(grp_props)
                    grp_props.update(params)
                props.update(params)

                axis = props.pop('axis', None)
                axis = axis or self.axis or self.subplot(row=1, column=1)

                yield axis, group_df, props, group_props
        else:
            axis = self.axis or self.subplot(row=1, column=1)
            yield axis, df, {**params}, {**params}

    def start_plot(self):
        return self

    def end_plot(self):
        return self.figure

    def subplot(
            self,
            row: int = 1,
            column: int = 1,
            axis: Union[str, int] = None,
            label: str = None,
            invert_axes: str = None,
            **kwargs) -> Axis:
        if self.axes and axis:
            self.axis = self.axes[axis]
            return self.axis
        if not column:
            index = row - 1
            row = (index // self.rows) + 1
            column = (index % self.columns) + 1
        label = label or '{}-{}'.format(row, column)
        index = (row - 1) * self.columns + column
        self.axis = self.figure.add_subplot(
            self.rows, self.columns, index, label=label, **kwargs)
        if invert_axes or self.settings['axis'].get('invert_axes'):
            if not self.axis.xaxis_inverted():
                self.axis.invert_xaxis()
            if not self.axis.yaxis_inverted():
                self.axis.invert_yaxis()
        return self.axis

    def _update_legend(
            self,
            legend_id: str,
            group_props: dict,
            artist: Artist):
        for group in group_props:
            for label in group_props[group]:
                self.plot_legend.add_entry(
                    legend_id, group, label, artist(**group_props[group][label]))

    def legend(self, legend=None, group=None, labels=None, **kwargs):
        """Add a legend to the current axis.
        """

        with self.settings.scope(legend={**kwargs}):
            axis = self.axis
            options = self.settings['legend']
            artist = self.legends.make_legend_artist(legend, group, labels, **options)
            axis.add_artist(artist)

    def data(self, data=None, x=None, y=None, **kwargs):
        self.settings.push(data=dict(data=data, x=x, y=y, **kwargs))

    def markers(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            where: str = 'all',
            legend: str = None,
            **kwargs) -> 'VowelPlot':

        artist = MarkerArtist()
        with self.settings.scope(
                data=dict(
                    data=data,
                    x=x,
                    y=y,
                    where=where),
                legend=legend if isinstance(legend, dict) else {},
                markers={**kwargs}):

            settings = self.settings['data', 'markers', 'legend']

            legend_id = legend or generate_legend_id('markers')

            for axis, group_df, props, group_props in self.groups_iterator(
                    settings['data'], settings['markers']):

                x = group_df[settings['data']['x']]
                y = group_df[settings['data']['y']]
                artist.plot(axis, x, y, **props)

                if legend:
                    self._update_legend(
                        legend_id,
                        group_props,
                        artist.legend)

        return self

    def labels(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            where: str = 'all',
            label_by: str = None,
            **kwargs) -> 'VowelPlot':

        artist = LabelArtist()

        with self.settings.scope(
                data=dict(
                    data=data,
                    x=x,
                    y=y,
                    where=where),
                labels=dict(label_by=label_by, **kwargs)):

            settings = self.settings['data', 'labels']
            bounds = BoundingBox()
            for axis, group_df, props, _group_props in self.groups_iterator(
                    settings['data'], settings['labels']):

                x = group_df[settings['data']['x']]
                y = group_df[settings['data']['y']]
                bounds.update_from_xy(x=x.values, y=y.values)
                bounds.update_axis_bounds(axis)

                labels = group_df[settings['labels']['label_by']]
                artist.plot(axis, x, y, labels, **props)

        return self

    def polygons(
            self,
            point: Union[str, int],
            points: list = None,
            where: Union[str, types.FunctionType] = None,
            closed: bool = True,
            hull=True,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            legend: Union[str, bool] = False,
            **kwargs) -> 'VowelPlot':
        """
        Add a polygon to the plot
        """

        artist = PolygonArtist()
        with self.settings.scope(
                data=dict(
                    data=data,
                    x=x,
                    y=y),
                polygon=dict(**kwargs)):

            settings = self.settings['data', 'polygon']

            data = settings['data']['data']
            x = settings['data']['x']
            y = settings['data']['y']

            if where:
                data = aggregate_df(data, [x, y], point, where)
            bounds = BoundingBox()
            legend_id = legend or generate_legend_id('polygons')
            for axis, group_df, props, group_props in self.groups_iterator(
                    settings['data'], settings['polygons']):
                xy = []
                if points:
                    hull = False
                    for p in points:
                        i = group_df[point] == p
                        group_x = group_df[i, x].mean()
                        group_y = group_df[i, y].mean()
                    group_df = group_df[group_df[point].isin(points)]
                    xy.append((group_x, group_y))
                if hull:
                    coords = np.atleast_2d(group_df[[x, y, point]].values)
                    convex_hull = MultiPoint(coords).convex_hull.exterior.coords[:]
                    xy.extend([(x, y) for x, y in convex_hull])
                artist.plot(axis, xy, closed=closed, **props)

                bounds.update_from_xy(xy)
                bounds.update_axis_bounds(axis)
                if legend:
                    self._update_legend(
                        legend_id,
                        group_props,
                        artist.legend)

        return self

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
        artist = EllipseArtist()

        with self.settings.scope(
                data=dict(
                    data=data,
                    x=x,
                    y=y),
                legend=legend if isinstance(legend, dict) else {},
                ellipses={**kwargs}):

            settings = self.settings['data', 'ellipses']

            legend_id = legend if isinstance(
                legend, str) else generate_legend_id('ellipses')

            bounds = BoundingBox()
            for axis, group_df, props, group_props in self.groups_iterator(
                    settings['data'], settings['ellipses']):

                group_x = group_df[settings['data']['x']]
                group_y = group_df[settings['data']['y']]
                center_x, center_y, width, height, angle = get_confidence_ellipse(
                    group_x, group_y, confidence=confidence, n_std=n_std, n_mad=n_mad)
                artist.plot(axis, (center_x, center_y), width, height, angle, **props)

                bounds.update_from_xy(
                    x=[center_x - width / 2, center_x + width / 2],
                    y=[center_y - height / 2, center_y - width / 2])
                bounds.update_axis_bounds(axis)

                if legend:
                    self._update_legend(legend_id, group_props,
                                        artist.legend)

        return self

    def contours(
            self,
            data: pd.DataFrame = None,
            x: str = None,
            y: str = None,
            levels: int = 10,
            samples: int = 50,
            legend: str = '',
            ** kwargs):
        """Add contour plots around formant data.


        """
        artist = ContourArtist()

        with self.settings.scope(
                data=dict(
                    data=data,
                    x=x,
                    y=y),
                legend=legend if isinstance(legend, dict) else {},
                contour={**kwargs}):

            settings = self.settings['data', 'contour']

            legend_id = legend or generate_legend_id('contour')

            for axis, group_df, props, group_props in self.groups_iterator(
                    settings['data'], settings['contour']):

                x = group_df[settings['data']['x']]
                y = group_df[settings['data']['y']]

                kernel = st.gaussian_kde(np.array([x, y]).T)

                cx, cy = np.meshgrid(
                    np.linspace(x.min(), x.max(), num=samples),
                    np.linspace(y.min(), y.max(), num=samples),
                    indexing='xy')

                xy = np.array([x.ravel(), y.ravel()]).T
                cz = kernel(xy).reshape((samples, samples))

                artist.plot(cx, cy, cz, levels=levels, **props)
                axis.relim()
                axis.autoscale_view()

                if legend:
                    self._update_legend(legend_id, group_props,
                                        artist.legend)

        return self

    def lines(self,
              data: pd.DataFrame,
              points: List[Tuple[str, str]] = None,
              start: Tuple[str, str] = None,
              end: Tuple[str, str] = None,
              arrows: Union[str, Tuple[FancierArrow, FancierArrow]] = None,
              where: str = None,
              legend: str = '',
              **kwargs):
        """Add lines to the plot.
        """

        points = points or [start, end]

        columns = np.unique(np.array(points).flatten())

        artist = LineArtist()

        with self.settings.scope(
                data=dict(
                    data=data,
                    where=None),
                legend=legend if isinstance(legend, dict) else {},
                lines={**kwargs}):

            settings = self.settings['data', 'lines', 'legend']

            legend_id = legend or generate_legend_id('lines')

            for axis, group_df, props, group_props in self.groups_iterator(
                    settings['data'], settings['lines']):

                if where:
                    group_df = aggregate_df(group_df, columns, [], where=where)
                data_points = [(group_df[x], group_df[y]) for x, y in points]
                artist.plot(axis, data_points, arrows, **props)

                if legend:
                    self._update_legend(
                        legend_id,
                        group_props,
                        artist.legend)
