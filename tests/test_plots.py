"""
Tests for the plots module.
"""

import unittest

from matplotlib.cm import get_cmap
import numpy as np

from vlnm.plots import (
    get_color_list,
    get_color_map,
    get_confidence_ellipse_params,
    get_marker_map)


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


class TestGetConfidenceEllipseParams(unittest.TestCase):
    """Tests for the get_confidence_ellipse_params."""

    def test_no_data(self):
        """No data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse_params([], [])

    def test_different_size_data(self):
        """Different sized data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse_params([0, 1], [0, 1, 2])

    def test_too_little_data(self):
        """Too little data raises error."""
        with self.assertRaises(ValueError):
            get_confidence_ellipse_params([0, 1], [0, 1])

    def test_data(self):
        """Sunny day test."""
        width, height, angle = get_confidence_ellipse_params(
            [-1, -2, 1, 2], [-2, -1, 2, 1])
        self.assertAlmostEqual(width, 12, delta=0.01)
        self.assertAlmostEqual(height, 4, delta=0.01)
        self.assertAlmostEqual(angle, 45, 2)
