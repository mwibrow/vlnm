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

    def test_list_mapping(self):
        """List mapping returns correct value"""
        expected = {
            'w': 'a',
            'x': 'b',
            'y': 'c',
            'z': 'd',
        }
        mapper = Mapper(list(expected.values()))
        actual = {data: mapper.get_value(data) for data in expected}
        self.assertDictEqual(actual, expected)

    def test_list_mapping_default(self):
        """List mapping returns correct default value"""
        expected = {
            'w': 'a',
            'x': 'b',
            'y': 'c',
            'z': 'd',
            'q': 'p',
        }
        mapper = Mapper(['a', 'b', 'c', 'd'], default='p')
        actual = {data: mapper.get_value(data) for data in ['w', 'x', 'y', 'z', 'q']}
        self.assertDictEqual(actual, expected)

    def test_list_mapping_cycle(self):
        """List mapping cycles values"""
        expected = {
            'w': 'a',
            'x': 'b',
            'y': 'c',
            'z': 'd',
            'q': 'a',
        }
        mapper = Mapper(['a', 'b', 'c', 'd'], cycle=True)
        actual = {data: mapper.get_value(data) for data in ['w', 'x', 'y', 'z', 'q']}
        self.assertDictEqual(actual, expected)

    def test_dict_mapping(self):
        """dict mapping returns correct value"""
        expected = {
            'w': 'a',
            'x': 'b',
            'y': 'c',
            'z': 'd',
        }
        mapper = Mapper(expected)
        actual = {data: mapper.get_value(data) for data in expected}
        self.assertDictEqual(actual, expected)

    def test_dict_mapping_default(self):
        """dict mapping returns correct default value"""
        mapping = {
            'w': 'a',
            'x': 'b',
            'y': 'c',
            'z': 'd',
        }
        mapper = Mapper(mapping, default='q')
        actual = {data: mapper.get_value(data) for data in ['w', 'x', 'y', 'z', 'p']}
        self.assertDictEqual(actual, {'p': 'q', **mapping})
