"""
Tests for the plots module.
"""

import os
import unittest
from unittest.mock import MagicMock, Mock, patch

from matplotlib.cm import get_cmap
from matplotlib.font_manager import FontManager, FontProperties
import numpy as np
import pandas as pd

from vlnm.plots import (
    get_color_map,
    get_confidence_ellipse,
    get_font_map,
    get_marker_map,
    VowelPlot)

from tests import FIXTURES
from tests.helpers import assert_series_equal

class TestGetColorMap(unittest.TestCase):
    """
    Tests for the get_color_map function.
    """

    def test_empty_color_list(self):
        """No colors returns dict with colors set to None."""
        expected = dict(had=None)
        actual = get_color_map([], ['had'])
        self.assertDictEqual(actual, expected)

    def test_empty_category_list(self):
        """No categories returns empty dict."""
        expected = {}
        actual = get_color_map(['black'], [])
        self.assertDictEqual(actual, expected)

    def test_list_argument(self):
        """Return correct map using list argument."""
        expected = dict(had='red', head='green', hod='blue')
        actual = get_color_map(['red', 'green', 'blue'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_string_color(self):
        """String color returns same color for each category."""
        expected = dict(had='red', head='red', hod='red')
        actual = get_color_map('red', ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_colormap_name(self):
        """String colormap name returns colors."""

        color_map = get_color_map('tab20', ['had', 'head', 'hod'])
        self.assertEqual(len(color_map), 3)
        for color in color_map.values():
            self.assertIsInstance(color, np.ndarray)
            self.assertEqual(len(color), 4)

    def test_colormap_instance(self):
        """Colormap instance returns colors."""
        cmap = get_cmap('tab20', 3)
        color_map = get_color_map(cmap, ['had', 'head', 'hod'])
        self.assertEqual(len(color_map), 3)
        for color in color_map.values():
            self.assertIsInstance(color, np.ndarray)
            self.assertEqual(len(color), 4)

    def test_colormap_instance_expande(self):
        """Colormap with too-few colors, expands colors."""
        cmap = get_cmap('tab20', 2)
        self.assertEqual(len(cmap.colors), 2)

        color_map = get_color_map(cmap, ['had', 'head', 'hod'])
        self.assertEqual(len(color_map), 3)
        for color in color_map.values():
            self.assertIsInstance(color, np.ndarray)
            self.assertEqual(len(color), 4)

    def test_recycling(self):
        """Colors recycled when fewer colors than categories."""
        expected = dict(had='red', head='green', hod='red')
        actual = get_color_map(['red', 'green'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)


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


class TestGetMarkerMap(unittest.TestCase):
    """Tests for the get_marker_map function."""

    def test_empty_marker_list(self):
        """No marker returns dict with markers set to None."""
        expected = dict(had=None)
        actual = get_marker_map([], ['had'])
        self.assertDictEqual(actual, expected)

    def test_empty_category_list(self):
        """No categories returns empty dict."""
        expected = {}
        actual = get_marker_map(['black'], [])
        self.assertDictEqual(actual, expected)

    def test_list_argument(self):
        """Return correct map using list argument."""
        expected = dict(had='.', head='^', hod='s')
        actual = get_color_map(['.', '^', 's'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_string_marker(self):
        """String marker returns same marker for each category."""
        expected = dict(had='.', head='.', hod='.')
        actual = get_color_map('.', ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_recycling(self):
        """Markers recycled when fewer markers than categories."""
        expected = dict(had='.', head='^', hod='.')
        actual = get_color_map(['.', '^'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)


class TestGetFontMap(unittest.TestCase):
    """Tests for the get_font_map function."""

    @classmethod
    def setUpClass(cls):
        manager = FontManager()
        cls.fonts = manager.ttflist

    def test_empty_font_list(self):
        """No marker returns dict with fonts set to default font propeties."""
        expected = dict(had=FontProperties())
        actual = get_font_map([], ['had'])
        self.assertDictEqual(actual, expected)

    def test_empty_category_list(self):
        """No categories returns empty dict."""
        expected = {}
        actual = get_font_map(['black'], [])
        self.assertDictEqual(actual, expected)

    def test_list_argument(self):
        """Return correct map using list argument."""
        fonts = self.fonts[:3]
        font_properties = [FontProperties(fname=font.fname) for font in fonts]
        expected = dict(
            had=font_properties[0],
            head=font_properties[1],
            hod=font_properties[2])
        actual = get_color_map(font_properties, ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_string_font(self):
        """String font gets font by name."""
        font = self.fonts[0]
        name = font.name
        font_properties = FontProperties(family=name)
        expected = dict(
            had=font_properties,
            head=font_properties,
            hod=font_properties)
        actual = get_font_map(name, ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_font_path(self):
        """Font path gets font by path."""
        font = self.fonts[0]
        fname = font.fname
        font_properties = FontProperties(fname=fname)
        expected = dict(
            had=font_properties,
            head=font_properties,
            hod=font_properties)
        actual = get_font_map(fname, ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_recycling(self):
        """Fonts recycled when fewer fonts than categories."""
        fonts = self.fonts[:2]
        font_properties = [FontProperties(fname=font.fname) for font in fonts]
        expected = dict(
            had=font_properties[0],
            head=font_properties[1],
            hod=font_properties[0])
        actual = get_color_map(font_properties, ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)


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
