"""
    Plotting module
    ~~~~~~~~~~~~~~~
"""
from collections import OrderedDict

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

from vlnm.plotting.utils import (
    context_from_kwargs,
    create_figure,
    merge,
    merge_contexts,
    strip,
    translate_props)
from vlnm.plotting.mappers import get_prop_mapper


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
            data=None,
            x=None,
            y=None,
            rows: int = 1,
            columns: int = 1,
            width: float = 4,
            height: float = 4,
            figure: Figure = None,
            **kwargs):
        figsize = kwargs.pop('figsize', (width, height) if width and height else None)
        self.figure = figure or create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.plot_context = strip(dict(data=data, x=x, y=y, invert_axes=True))
        self.axis = None
        self.legends = {}

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

    def __call__(**kwargs):
        return self.context(**kwargs)

    def context(self, **kwargs):
        self.plot_context = merge(self.plot_context, kwargs)
        return self

    def start_plot(self):
        return self

    def end_plot(self):
        if 'invert_axes' in self.plot_context:
            axes = self.figure.get_axes()
            for axis in axes:
                if not axis.xaxis_inverted():
                    axis.invert_xaxis()
                if not axis.yaxis_inverted():
                    axis.invert_yaxis()
        return self.figure

    def subplot(self, row=None, column=None, label=None, **kwargs):
        if not column:
            index = row - 1
            row = (index // self.rows) + 1
            column = (index % self.columns) + 1
        label = label or '{}-{}'.format(row, column)
        index = (row - 1) * self.columns + column
        self.axis = self.figure.add_subplot(
            self.rows, self.columns, index, label=label, **kwargs)
        return self.axis

    def _df_iterator(self, context):

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
            columns = [x, y]
            if where == 'mean':
                df = df.groupby(groups, as_index=True).apply(
                    lambda group_df: group_df[columns].mean(axis=0))
                df = df.reset_index()
            elif where == 'median':
                df = df.groupby(groups, as_index=True).apply(
                    lambda group_df: group_df[columns].median(axis=0))
                df = df.reset_index()

        # Get property mappers.
        for key, value in context.items():
            if key.endswith('_by'):
                prop = key[:-3]
                group = value
                mapping = context[prop]
                if prop == 'plot':
                    plot_mapper[group] = get_prop_mapper(prop, mapping=mapping, data=df[group])
                else:
                    prop_mappers[group] = get_prop_mapper(prop, mapping=mapping, data=df[group])

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
                    mapped_props = prop_mappers[group].get_props(value)
                    mapped_props.update(**context.get('_params', {}))
                    group_props[group] = group_props.get(group, OrderedDict())
                    group_props[group][value] = merge(params, mapped_props)
                    props.update(**mapped_props)
                if group in plot_mapper:
                    plot_props = plot_mapper[group].get_props(value)

            if plot_props:
                axis = self.subplot(**plot_props)
            else:
                axis = self.axis or self.subplot(row=1, column=1)

            yield axis, group_df, props, group_values, group_props

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
        if not legend_ids:
            return
        legend_id = legend_id or legend_ids[0]
        legend = self.legends[legend_id]

        if 'handler_map' not in kwargs:
            kwargs['handler_map'] = {
                mpatches.Ellipse: _HandlerEllipse()
            }
        title = kwargs.pop('title', [])
        if isinstance(title, str):
            title = [title]
        for i, group in enumerate(legend):
            handles = list(legend[group].values())
            labels = list(legend[group].keys())
            legend_artist = plt.legend(
                handles=handles,
                labels=labels,
                title=title[i] if title else group,
                **kwargs)
            self.axis.add_artist(legend_artist)

    def markers(self, data=None, x=None, y=None, where='all', legend=None, **kwargs):
        context, params = context_from_kwargs(kwargs)

        context = merge_contexts(
            self.plot_context,
            context,
            dict(data=data, x=x, y=y, where=where, _params=params))

        plotter = MarkerPlotter()

        for axis, group_df, props, group_values, group_props in self._df_iterator(context):
            x = group_df[context['x']]
            y = group_df[context['y']]
            plotter.plot(axis, x, y, **props)

            if legend:
                self._update_legend(legend, group_props, plotter.legend_artist)

        return self


class Plotter:

    defaults = {}
    prop_translator = {}

    def __init__(self, defaults=None):
        self.defaults = defaults or self.__class__.defaults or {}

    def translate_props(self, props, translator=None):
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
                        translated[translation] = value
            else:
                translated[prop] = value
        return translated


class MarkerPlotter(Plotter):

    defaults = {
        'marker': '.',
        'color': 'black',
        'size': 1
    }

    prop_translator = {
        'color': ['edgecolor', 'facecolor'],
        'size': 's'
    }

    def legend_artist(self, **kwargs):
        props = self.defaults.copy()
        props.update(**kwargs)
        props = self.translate_props(props)
        props = self.translate_props(props, {
            's': 'markersize',
            'edgecolor': 'markeredgecolor',
            'facecolor': 'markerfacecolor',
            'linewidth': 'markeredgewidth'})
        if 'markersize' in props:
            del props['markersize']
        return Line2D(
            [0], [0], linestyle='', drawstyle=None, **props)

    def plot(self, axis, x, y, **kwargs):
        props = self.defaults.copy()
        props.update(**kwargs)
        props = self.translate_props(props)
        axis.scatter(x, y, **props)


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
