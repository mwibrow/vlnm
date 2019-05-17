"""
    Plotting module
    ~~~~~~~~~~~~~~~
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import vlnm.utils


def create_figure(*args, **kwargs) -> Figure:
    return plt.figure(*args, **kwargs)


class VowelPlot:
    """
    Class for managing vowel plots.


    Examples
    --------

    .. ipython::

        from vlnm import pb1952, VowelPlot

        df = pb1952()

        with VowelPlot(data=df, x='f2', y='f1', width=5, height=5) as plot:

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

        self.plot_context = utils.strip(dict(data=data, x=x, y=y))
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

    def __exit__(*args):
        return self.end_plot()

    def __call__(**kwargs):
        return self.context(**kwargs)

    def context(self, **kwargs):
        self.plot_context = utils.merge(self.plot_context, kwargs)
        return self

    def subplot(self, row=None, column=None, label=None):
        if not column:
            index = row - 1
            row = (index // self.rows) + 1
            column = (index % self.columns) + 1
        label = label or '{}-{}'.format(row, column)
        index = (row - 1) * self.columns + column
        self.axis = self.figure.subplot(self.rows, self.columns, index, label=label)
        return self.axis

    def df_generator(self, df, context):

        groups = []
        params = utils.merge(self.plot_context, context)
        prop_mappers = {}
        plot_mapper = {}
        bys = [key for key in context if key.endswith('_by')]
        for by in bys:
            prop = by[:-3]
            group = params.pop(by)
            mapping = params.pop('{}s'.format(prop))
            if not group in groups:
                group.append(groups)
            if prop == 'plot':
                plot_mapper[group] = get_prop_mapper(prop, df[group])
            else:
                prop_mappers[group] = get_prop_mapper(prop, df[group])

        x = params.pop('x')
        y = params.pop('y')
        grouped = df.groupby(groups, as_index=False)
        for values, group_df in grouped:
            values = values if isinstance(values, tuple) else (values,)
            group_props = params.copy()
            plot_props = {}
            group_values = {}
            for group, value in zip(groups, values):
                group_values[group] = value
                if group in prop_mappers:
                    group_props.update(**prop_mappers[group].get_props(value))
                if group in plot_mapper:
                    plot_props = plot_mapper[group].get_props(value)

            if plot_props:
                axis = self.subplot(**plot_props)
            else:
                axis = self.axis

            yield axis, group_df[x], group_df[y], group_values, group_props
