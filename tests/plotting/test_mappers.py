"""
Tests for the vlnm.plotting.mappers module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

import pandas as pd

from vlnm.plotting.mappers import (
    unique
)


class TestUnique(unittest.TestCase):
    """Tests for the unique function"""

    def test_empty_data(self):
        """Empty data returns empty list."""
        self.assertListEqual([], unique([]))

    def test_list(self):
        """Return uniques"""
        expected = ['a', 'z', 'k', 'l']
        actual = unique(expected * 10, sort=True)
        self.assertListEqual(actual, sorted(expected))

    def test_series(self):
        """Uniques returned from pandas series"""
        expected = ['a', 'z', 'k', 'l']
        series = pd.Series(expected[::-1] * 10)
        actual = unique(series)
        self.assertListEqual(actual, sorted(expected))

    def test_categorical(self):
        """Pandas categorical returned in level order"""
        expected = ['a', 'z', 'k', 'l']
        series = pd.Series(expected[::-1] * 10).astype('category')
        series.cat.categories = expected
        actual = unique(series)
        self.assertListEqual(actual, expected)
