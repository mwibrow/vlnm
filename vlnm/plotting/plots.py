"""
    Plotting module
    ~~~~~~~~~~~~~~~
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def create_figure(*args, **kwargs) -> Figure:
    return plt.figure(*args, **kwargs)


class VowelPlot:
    """
    Class for managing vowel plots.

    """

    def __init__(
            self,
            rows: int = 1,
            columns: int = 1,
            width: float = 4,
            height: float = 4,
            figure: Figure = None,
            **kwargs):
        figsize = (width, height) if width and height else None
        self.figure = figure or create_figure(figsize=figsize, **kwargs)
        self.width, self.height = self.figure.get_size_inches()
        self.rows, self.columns = rows, columns

        self.plot_context = context or {}
        self.axis = None
        self.legends = {}

    def __getattr__(self, attr):
        if hasattr(self.axis, attr):
            return getattr(self.axis, attr)
        if hasattr(plt, attr):
            return getattr(plt, attr)
        return object.__getattribute__(self, attr)

    def __enter__(self):
        return self.start_plot()

    def __exit__(*args):
        return self.end_plot()

    def subplot(self, row=None, column=None, label=None):
        if not column:
            index = row - 1
            row = (index // self.rows) + 1
            column = (index % self.columns) + 1
        label = label or '{}-{}'.format(row, column)
        index = (row - 1) * self.columns + column
        self.axis = self.figure.subplot(self.rows, self.columns, index, label=label)
        return self.axis
