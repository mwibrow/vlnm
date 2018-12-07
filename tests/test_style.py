"""
tests for the vlnm.plotting.style module
"""

import unittest

from matplotlib.cm import get_cmap
import numpy as np

from vlnm.plotting.style import (
    get_color_map,
    get_line_map,
    get_marker_map,
    get_group_styles,
    STYLES)


class TestGetGroupStyle(unittest.TestCase):
    """Tests for the get_group_style function."""

    def test_no_groups(self):
        """No groups returns empty style."""
        expected = {}
        actual = get_group_styles(
            [], ('had',), dict(color='vowel'), dict(color=dict(had='black')))
        self.assertEqual(actual, expected)

    def test_no_values(self):
        """No values returns empty style."""
        expected = {}
        actual = get_group_styles(
            ['vowel'], (), dict(color='vowel'), dict(color=dict(had='black')))
        self.assertEqual(actual, expected)

    def test_single_style(self):
        """Correct style returned."""
        expected = dict(color='blue')
        actual = get_group_styles(
            ['vowel'], ('had',),
            dict(color='vowel'), dict(color=dict(had='blue')))
        self.assertEqual(actual, expected)

    def test_multilples_styles(self):
        """Correct styles returned."""
        expected = dict(color='blue', marker='.', line='-')
        actual = get_group_styles(
            ['vowel', 'gender', 'participant'], ('had', 'F', 'S1'),
            dict(color='vowel', marker='gender', line='participant'),
            dict(
                color=dict(had='blue'),
                marker=dict(F='.'),
                line=dict(S1='-')))
        self.assertEqual(actual, expected)

    def test_column_not_in_group(self):
        """Default style returned."""
        expected = dict()
        actual = get_group_styles(
            ['vowel'], ('heard',),
            dict(color='participant'), dict(color=dict(had='blue')))
        self.assertEqual(actual, expected)


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


class TestGetLineMap(unittest.TestCase):
    """Tests for the get_line_map function."""

    def test_empty_line_list(self):
        """No marker returns dict with markers set to None."""
        expected = dict(had=None)
        actual = get_line_map([], ['had'])
        self.assertDictEqual(actual, expected)

    def test_empty_category_list(self):
        """No categories returns empty dict."""
        expected = {}
        actual = get_line_map(['-'], [])
        self.assertDictEqual(actual, expected)

    def test_list_argument(self):
        """Return correct map using list argument."""
        expected = dict(had='-', head=':', hod='--')
        actual = get_line_map(['-', ':', '--'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_string_line(self):
        """String line returns same marker for each category."""
        expected = dict(had='-', head='-', hod='-')
        actual = get_line_map('-', ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)

    def test_recycling(self):
        """Markers recycled when fewer markers than categories."""
        expected = dict(had='-', head=':', hod='-')
        actual = get_line_map(['-', ':'], ['had', 'head', 'hod'])
        self.assertDictEqual(actual, expected)
