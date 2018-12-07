"""
Tests for the plots module.
"""

import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from matplotlib.cm import get_cmap
import numpy as np
import pandas as pd

from vlnm.plots import (
    get_confidence_ellipse,
    VowelPlot)
from vlnm.plotting.style import (
    get_color_map,
    get_marker_map
)
from tests import FIXTURES
from tests.helpers import assert_series_equal




class TestGetConfidenceEllipse(unittest.TestCase):
    """Tests for the get_confidence_ellipse_params."""

    def test_no_data(self):
        """No data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse([], [])

    def test_different_size_data(self):
        """Different sized data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse([0, 1], [0, 1, 2])

    def test_too_little_data(self):
        """Too little data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse([0, 1], [0, 1])

    def test_data(self):
        """Sunny day test."""
        x, y, width, height, angle = get_confidence_ellipse(
            [-1, -2, 1, 2], [-2, -1, 2, 1])
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertAlmostEqual(width, 12, delta=0.01)
        self.assertAlmostEqual(height, 4, delta=0.01)
        self.assertAlmostEqual(angle, 45, 2)


def mock_axis() -> MagicMock:
    """Make a mock axis."""
    axis = MagicMock()
    axis.scatter = Mock()
    axis.annotation = Mock()
    axis.add_artist = Mock()
    return axis

class TestVowelPlot(unittest.TestCase):
    """Tests for the VowelPlot class."""

    def setUp(self):
        self.df = pd.read_csv(
            os.path.join(FIXTURES, 'hawkins_midgely_2005.csv'))


    @patch('vlnm.plots._create_figure')
    def test_init(self, mock_create_figure):  # pylint: disable=no-self-use
        """Test initialisation."""
        width, height = 4, 3
        figure = MagicMock()
        mock_create_figure.return_value = figure
        figure.get_size_inches = Mock(return_value=(width, height))

        VowelPlot(width=width, height=height)
        mock_create_figure.assert_called_with(figsize=(width, height))

    def test_subplot_noarg(self):
        """Test subplot method without arg."""
        plot = VowelPlot(width=4, height=3)
        plot.subplot()
        axes = plot.figure.get_axes()
        self.assertEqual(len(axes), 1)

    def test_1x1_subplot_axes(self):
        """Test multiple 1x1 subplot calls returns same axis."""
        plot = VowelPlot(rows=1, columns=1)
        subplot1 = plot.subplot()
        subplot2 = plot.subplot()
        axes = plot.figure.get_axes()
        self.assertEqual(len(axes), 1)
        self.assertEqual(id(subplot1), id(subplot2))

    def test_1x2_subplot_axes(self):
        """Test multiple 2x1 subplot calls returns different axes."""
        plot = VowelPlot(rows=1, columns=2)
        subplot1 = plot.subplot()
        subplot2 = plot.subplot()
        axes = plot.figure.get_axes()
        self.assertEqual(len(axes), 2)
        self.assertNotEqual(id(subplot1), id(subplot2))

    def test_context_manager(self):
        """Test context manager creates axis."""
        plot = VowelPlot()
        with plot:
            pass
        axes = plot.figure.get_axes()
        self.assertEqual(len(axes), 1)

class TestVowelPlotMarkers(unittest.TestCase):
    """Tests for the VowelPlot.markers method."""

    def setUp(self):
        self.df = pd.read_csv(
            os.path.join(FIXTURES, 'hawkins_midgely_2005.csv'))

        width, height = 4, 3
        axis = MagicMock()
        axis.scatter = MagicMock()
        figure = MagicMock()
        figure.get_size_inches = Mock(return_value=(width, height))
        figure.add_subplot = MagicMock(return_value=axis)

        self.width = width
        self.height = height
        self.figure = figure


    @patch('vlnm.plots._create_figure')
    def test_markers(self, mock_create_figure):
        """Test call arguments for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(data=self.df, x='f2', y='f1', vowel='vowel')

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        cmap = get_color_map('tab20', vowels)
        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertListEqual(
                list(kwargs['c']), list(cmap[vowels[i]]))
            x = self.df[self.df['vowel'] == vowels[i]]['f2']
            y = self.df[self.df['vowel'] == vowels[i]]['f1']
            assert_series_equal(args[0], x)
            assert_series_equal(args[1], y)

    @patch('vlnm.plots._create_figure')
    def test_markers_legend(self, mock_create_figure):
        """Test call arguments with legend for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(
                data=self.df, x='f2', y='f1', vowel='vowel', legend=True)

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        cmap = get_color_map('tab20', vowels)
        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertListEqual(
                list(kwargs['c']), list(cmap[vowels[i]]))
            self.assertEqual(kwargs['label'], vowels[i])
            x = self.df[self.df['vowel'] == vowels[i]]['f2']
            y = self.df[self.df['vowel'] == vowels[i]]['f1']
            assert_series_equal(args[0], x)
            assert_series_equal(args[1], y)

    @patch('vlnm.plots._create_figure')
    def test_markers_which_mean(self, mock_create_figure):
        """Test which='mean' for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(
                data=self.df, x='f2', y='f1', vowel='vowel', which='mean')

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        cmap = get_color_map('tab20', vowels)
        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertListEqual(
                list(kwargs['c']), list(cmap[vowels[i]]))
            x = self.df[self.df['vowel'] == vowels[i]]['f2'].mean()
            y = self.df[self.df['vowel'] == vowels[i]]['f1'].mean()
            self.assertEqual(args[0].values[0], x)
            self.assertEqual(args[1].values[0], y)

    @patch('vlnm.plots._create_figure')
    def test_markers_which_median(self, mock_create_figure):
        """Test which='median' for markers method."""
        mock_create_figure.return_value = self.figure

        plot = VowelPlot(width=self.width, height=self.height)
        vowels = sorted(self.df['vowel'].unique())
        with plot:
            plot.markers(
                data=self.df, x='f2', y='f1', vowel='vowel', which='median')

        axis = plot.axis
        self.assertEqual(axis.scatter.call_count, len(vowels))
        cmap = get_color_map('tab20', vowels)
        for i, kall in enumerate(axis.scatter.mock_calls):
            _, args, kwargs = kall
            self.assertEqual(kwargs['marker'], '.')
            self.assertListEqual(
                list(kwargs['c']), list(cmap[vowels[i]]))
            x = self.df[self.df['vowel'] == vowels[i]]['f2'].median()
            y = self.df[self.df['vowel'] == vowels[i]]['f1'].median()
            self.assertEqual(args[0].values[0], x)
            self.assertEqual(args[1].values[0], y)
