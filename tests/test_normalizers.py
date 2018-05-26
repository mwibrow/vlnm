"""
Tests for the normalizers library.
"""

import unittest

import numpy as np
import pandas as pd

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel
)
from vlnm.normalizers import (
    BarkNormalizer,
    ErbNormalizer,
    Log10Normalizer,
    LogNormalizer,
    MelNormalizer
)


class TestNormalizersValueError(unittest.TestCase):
    """
    Check normalizers raise ValueError if no formants specified.
    """

    def setUp(self):
        self.df = pd.DataFrame(dict(
            f1=[100, 200, 300],
            f2=[1100, 1200, 1300]
        ))

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        with self.assertRaises(ValueError):
            BarkNormalizer().normalize(self.df)

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        with self.assertRaises(ValueError):
            ErbNormalizer().normalize(self.df)

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        with self.assertRaises(ValueError):
            Log10Normalizer().normalize(self.df)

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        with self.assertRaises(ValueError):
            LogNormalizer().normalize(self.df)

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        with self.assertRaises(ValueError):
            MelNormalizer().normalize(self.df)


class TestSunnyDayNormalizers(unittest.TestCase):
    """
    Sunny day tests for normalizers
    """

    def setUp(self):
        self.df = pd.DataFrame(dict(
            f1=[100, 200, 300],
            f2=[1100, 1200, 1300]
        ))
        self.kwargs = dict(f1='f1', f2='f2')

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        expected = hz_to_bark(self.df.copy())
        actual = BarkNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        expected = hz_to_erb(self.df.copy())
        actual = ErbNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        expected = np.log10(self.df.copy())
        actual = Log10Normalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        expected = np.log(self.df.copy())
        actual = LogNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        expected = hz_to_mel(self.df.copy())
        actual = MelNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))



def make_new_columns_expected(df, suffix, transform):
    """Helper for class Test new columns"""
    tmp_df = transform(df.copy())
    tmp_df.columns = ['{}{}'.format(column, suffix) for column in tmp_df.columns]
    return pd.concat([df.copy(), tmp_df], axis=1)

class TestNewColumns(unittest.TestCase):
    """
    Test normalized formants as new columns.
    """

    def setUp(self):
        self.suffix = '_N'
        self.df = pd.DataFrame(dict(
            f1=[100, 200, 300],
            f2=[1100, 1200, 1300]
        ))
        self.kwargs = dict(f1='f1', f2='f2', suffix=self.suffix)

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_bark)
        actual = BarkNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_erb)
        actual = ErbNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, np.log10)
        actual = Log10Normalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, np.log)
        actual = LogNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_mel)
        actual = MelNormalizer(**self.kwargs).normalize(self.df)
        self.assertTrue(actual.equals(expected))
