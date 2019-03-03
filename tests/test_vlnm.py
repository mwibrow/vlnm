"""
Tests for the VLNM package.
"""

from io import StringIO
import os
import unittest

from vlnm import (
    normalize,
    read_csv)
from vlnm.normalizers.base import register_normalizer
from vlnm.normalizers.speaker import LobanovNormalizer

ROOT = os.path.dirname(__file__)


class TestNormalize(unittest.TestCase):
    """
    Test the normalize function.
    """

    def setUp(self):
        register_normalizer(LobanovNormalizer, 'lobanov')
        self.df = read_csv(
            os.path.join(ROOT, 'fixtures', 'hawkins_midgely_2005.csv'))

    def test_method_string(self):
        """
        Get dataframe string method.
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        df = normalize(self.df, method='lobanov')
        actual = list(df.columns)
        self.assertListEqual(actual, expected)

    def test_method_class(self):
        """
        Get dataframe from path using class method.
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        df = normalize(self.df, method=LobanovNormalizer)
        actual = list(df.columns)
        self.assertListEqual(actual, expected)

    def test_method_instance(self):
        """
        Get dataframe from path using instance method.
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        df = normalize(self.df, method=LobanovNormalizer())
        actual = list(df.columns)
        self.assertListEqual(actual, expected)

    def test_save_to_file(self):
        """
        Save output to file(-like object).
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        output = StringIO()
        normalize(self.df, output, method='lobanov')
        actual = output.getvalue().split('\n')[0].split(',')
        self.assertListEqual(actual, expected)


class TestReadCSV(unittest.TestCase):
    """
    Tests for the read_csv function.
    """

    def test_read(self):
        """
        Read file with path.
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        df = read_csv(os.path.join(
            ROOT, 'fixtures', 'hawkins_midgely_2005.csv'))
        actual = list(df.columns)
        self.assertListEqual(actual, expected)

    def test_read_data_dir(self):
        """
        Read file with data_dir.
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        df = read_csv(
            'hawkins_midgely_2005.csv',
            data_dir=os.path.join(ROOT, 'fixtures'))
        actual = list(df.columns)
        self.assertListEqual(actual, expected)
