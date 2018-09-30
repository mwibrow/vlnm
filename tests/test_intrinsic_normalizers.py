"""
Tests for the formant intrinsic normalizers.
"""

import unittest

import numpy as np

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers.normalizers import (
    BarkNormalizer,
    ErbNormalizer,
    LogNormalizer,
    Log10Normalizer,
    MelNormalizer)

from tests.helpers import (
    concat_df,
    generate_data_frame)


def get_test_dataframe(speakers=8):
    """Generate a test dataframe."""
    df = generate_data_frame(
        speakers=speakers,
        genders=['M', 'F'],
        factors=dict(
            group=['HV', 'LV'],
            test=['pre', 'post'],
            vowel=['a', 'e', 'i', 'o', 'u']))
    return df


DATA_FRAME = get_test_dataframe()


class TestIntrinsicNormalizersSunnyDay(unittest.TestCase):
    """
    Sunny day tests for normalizers
    """

    def setUp(self):
        df = generate_data_frame(
            speakers=8,
            genders=['M', 'F'],
            factors=dict(
                group=['HV', 'LV'],
                test=['pre', 'post'],
                vowel=['a', 'e', 'i', 'o', 'u']))
        self.df = df.copy()[['f0', 'f1', 'f2', 'f3']]
        self.kwargs = dict(formants=['f0', 'f1', 'f2', 'f3'])

    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = hz_to_bark(self.df.copy())
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = hz_to_erb(self.df.copy())
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = np.log10(self.df.copy())
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = np.log(self.df.copy())
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = hz_to_mel(self.df.copy())
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))


class TestIntrinsicNormalizersAliasColumns(unittest.TestCase):
    """
    Sunny day tests for normalizers with aliased columns.
    """

    def setUp(self):
        df = generate_data_frame(
            speakers=8,
            genders=['M', 'F'],
            factors=dict(
                group=['HV', 'LV'],
                test=['pre', 'post'],
                vowel=['a', 'e', 'i', 'o', 'u']))
        self.df = df.copy()
        self.df['f0@50'] = self.df['f0']
        self.df = self.df.drop('f0', axis=1)

    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = hz_to_bark(expected['f0@50'])
        actual = BarkNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = hz_to_erb(expected['f0@50'])
        actual = ErbNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = self.df.copy()
        expected['f0@50'] = np.log10(expected['f0@50'])
        actual = Log10Normalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = np.log(expected['f0@50'])
        actual = LogNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = hz_to_mel(expected['f0@50'])
        actual = MelNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))


def rename_columns(df, rename, transform):
    """Helper for class Test new columns."""
    tmp_df = transform(df.copy())
    tmp_df.columns = [rename.format(column) for column in tmp_df.columns]
    return concat_df([df.copy(), tmp_df], axis=1)


class TestIntrinsicNormalizersNewColumns(unittest.TestCase):
    """
    Test normalized formants as new columns.
    """

    def setUp(self):
        self.rename = '{}_N'
        df = generate_data_frame(
            speakers=8,
            genders=['M', 'F'],
            factors=dict(
                group=['HV', 'LV'],
                test=['pre', 'post'],
                vowel=['a', 'e', 'i', 'o', 'u']))
        self.df = df.copy()[['f0', 'f1', 'f2', 'f3']]
        self.kwargs = dict(
            formants=['f0', 'f1', 'f2', 'f3'],
            rename=self.rename)

    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_bark)
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_erb)
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = rename_columns(
            self.df, self.rename, np.log10)
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = rename_columns(self.df, self.rename, np.log)
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_mel)
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))
