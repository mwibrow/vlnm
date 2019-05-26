"""
    Tests for the vlnm.plotting.plots module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from unittest.mock import MagicMock, Mock, patch

import matplotlib
matplotlib.use('agg')

from matplotlib.cm import get_cmap
import numpy as np
import pandas as pd

from vlnm.data import hm2005
from vlnm.plotting.plots import (
    create_figure,
    VowelPlot)

from tests.helpers import assert_series_equal


def mock_axis() -> MagicMock:
    """Make a mock axis."""
    axis = MagicMock()
    axis.scatter = Mock()
    axis.annotation = Mock()
    axis.add_artist = Mock()
    return axis


class TestVowelPlot(unittest.TestCase):
    """
    Tests for the VowelPlot class.
    """

    @patch('vlnm.plotting.plots.create_figure')
    def test_init(self, mock_create_figure):  # pylint: disable=no-self-use
        """Test initialisation."""
        width, height = 4, 3
        figure = MagicMock()
        mock_create_figure.return_value = figure
        figure.get_size_inches = Mock(return_value=(width, height))

        VowelPlot(width=width, height=height)
        mock_create_figure.assert_called_with(figsize=(width, height))


class TestVowelPlotMarkers(unittest.TestCase):
    """
    Tests for the VowelPlot.markers method.
    """

    def setUp(self):
        self.df = hm2005()

        self.df['vowel'] = pd.Categorical(
            self.df['vowel'],
            sorted(self.df['vowel'].unique()),
            True)

        width, height = 4, 3
        axis = MagicMock()
        axis.scatter = MagicMock()
        figure = MagicMock()
        figure.get_size_inches = Mock(return_value=(width, height))
        figure.add_subplot = MagicMock(return_value=axis)

        self.width = width
        self.height = height
        self.figure = figure

    @patch('vlnm.plotting.plots.create_figure')
    def test_markers(self, mock_create_figure):
        """Test call arguments for markers method."""
        mock_create_figure.return_value = self.figure

        vowels = sorted(self.df['vowel'].unique())
        plot = VowelPlot(width=self.width, height=self.height)
        with plot:
            plot.markers(data=self.df, x='f2', y='f1', color_by='vowel', color='tab20')

        colors = get_cmap('tab20').colors

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))

        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall

            self.assertEqual(kwargs['marker'], '.')
            self.assertEqual(kwargs['edgecolor'], colors[i])
            self.assertEqual(kwargs['facecolor'], colors[i])
            x = self.df[self.df['vowel'] == vowels[i]]['f2']
            y = self.df[self.df['vowel'] == vowels[i]]['f1']
            assert_series_equal(args[0], x)
            assert_series_equal(args[1], y)

        self.assertEqual(0, len(axis.add_artist.mock_calls))

    @patch('vlnm.plotting.plots.create_figure')
    def test_markers_where_mean(self, mock_create_figure):
        """Test where='mean' for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(
                data=self.df, x='f2', y='f1', color_by='vowel', color='tab20', where='mean')

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        colors = get_cmap('tab20').colors

        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertEqual(kwargs['edgecolor'], colors[i])
            self.assertEqual(kwargs['facecolor'], colors[i])
            x = self.df[self.df['vowel'] == vowels[i]]['f2'].mean()
            y = self.df[self.df['vowel'] == vowels[i]]['f1'].mean()
            self.assertEqual(args[0].values[0], x)
            self.assertEqual(args[1].values[0], y)

    @patch('vlnm.plotting.plots.create_figure')
    def test_markers_where_median(self, mock_create_figure):
        """Test where='median' for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(
                data=self.df, x='f2', y='f1', color_by='vowel', color='tab20', where='median')

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        colors = get_cmap('tab20').colors

        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertEqual(kwargs['edgecolor'], colors[i])
            self.assertEqual(kwargs['facecolor'], colors[i])
            x = self.df[self.df['vowel'] == vowels[i]]['f2'].median()
            y = self.df[self.df['vowel'] == vowels[i]]['f1'].median()
            self.assertEqual(args[0].values[0], x)
            self.assertEqual(args[1].values[0], y)
