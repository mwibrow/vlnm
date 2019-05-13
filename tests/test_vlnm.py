"""
Tests for the VLNM package.
"""

from io import StringIO
import os
import unittest

from pandas import read_csv
from vlnm import normalize
from vlnm import register_normalizer
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

    def test_save_to_file(self):
        """
        Save output to file(-like object).
        """
        expected = ['speaker', 'f1', 'f2', 'vowel']
        output = StringIO()
        normalize(self.df, output, method='lobanov')
        actual = output.getvalue().split('\n')[0].split(',')
        self.assertListEqual(actual, expected)
