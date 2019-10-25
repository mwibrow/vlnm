"""
Tests for the vlnm.plotting.mappers module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

import pandas as pd

from vlnm.plotting.mappers import (
    unique,
    Mapper
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


class TestMapper(unittest.TestCase):
    """Tests for the Msapper class"""

    def test_init(self):  # pylint: disable=no-self-use
        """Initialse without error"""
        Mapper([])

    def test_init_with_mapper(self):
        """Initialise with existing Mapper instance"""
        mapper = Mapper(Mapper(['test'], cycle=False, default='test'))
        self.assertListEqual(mapper.values, ['test'])
        self.assertEqual(mapper.cycle, mapper.cycle)
        self.assertEqual(mapper.default, mapper.default)

    def test_get_value_callable(self):
        """Callable mapping returns correct value"""

        class _Mapping:
            def __init__(self):
                self.args = None
                self.kwargs = None

            def mapping(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
                return 'test'

            def __call__(self, *args, **kwargs):
                return self.mapping(*args, **kwargs)

        mapping = _Mapping()
        mapper = Mapper(mapping)
        value = mapper.get_value('any', 1, test='value')
        self.assertEqual(mapping.args, ('any', 1, ))
        self.assertDictEqual(mapping.kwargs, dict(test='value'))
        self.assertEqual(value, 'test')
