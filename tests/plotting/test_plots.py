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

from vlnm.plotting.plots import (
    create_figure,
    VowelPlot)


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
