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
        self.patcher = patch('vlnm.plotting.plots.MarkerArtist')
        self.mock_artist_class = self.patcher.start()
        self.mock_artist = MagicMock()
        self.mock_artist_class.return_value = self.mock_artist

        self.df = hm2005()
        self.plot = VowelPlot(data=self.df, x='f2', y='f1')

    def tearDown(self):
        self.patcher.stop()

    def test_calls(self):
        """Test number of calls"""
        with self.plot:
            self.plot.markers(color_by='vowel', color='tab20')
        self.assertTrue(self.mock_artist_class)
        self.assertEqual(
            self.mock_artist.plot.call_count,
            len(self.df['vowel'].unique()))

    def test_multiple_calls(self):
        """Test number of calls with multiple aesthetics"""
        with self.plot:
            self.plot.markers(
                color_by='vowel', color='tab20',
                marker_by='group', marker='.')
        self.assertTrue(self.mock_artist_class)

        expected = len(self.df['vowel'].unique()) * len(self.df['group'].unique())
        self.assertEqual(
            self.mock_artist.plot.call_count,
            expected)
