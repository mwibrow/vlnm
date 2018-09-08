"""
Tests for the normalize module.
"""

import unittest

import numpy as np
import pandas as pd

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers import (
    BarkNormalizer,
    ErbNormalizer,
    LogNormalizer,
    Log10Normalizer,
    MelNormalizer)

from tests.helpers import (
    generate_data_frame,
    repeat_test)


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

    @repeat_test()
    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = hz_to_bark(self.df.copy())
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = hz_to_erb(self.df.copy())
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = np.log10(self.df.copy())
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = np.log(self.df.copy())
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = hz_to_mel(self.df.copy())
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))



# def make_new_columns_expected(df, suffix, transform):
#     """Helper for class Test new columns."""
#     tmp_df = transform(df.copy())
#     tmp_df.columns = ['{}{}'.format(column, suffix) for column in tmp_df.columns]
#     return pd.concat([df.copy(), tmp_df], axis=1)

# class TestIntrinsicNormalizersNewColumns(unittest.TestCase):
#     """
#     Test normalized formants as new columns.
#     """

#     def setUp(self):
#         self.suffix = '_N'
#         df = generate_data_frame(
#             speakers=8,
#             genders=['M', 'F'],
#             factors=dict(
#                 group=['HV', 'LV'],
#                 test=['pre', 'post'],
#                 vowel=['a', 'e', 'i', 'o', 'u']))
#         self.df = df.copy()[['f0', 'f1', 'f2', 'f3']]
#         self.kwargs = dict(
#             formants=['f0', 'f1', 'f2', 'f3'],
#             suffix=self.suffix)

#     @repeat_test()
#     def test_bark_normalizer(self):
#         """Test BarkNormalizer."""
#         expected = make_new_columns_expected(self.df, self.suffix, hz_to_bark)
#         actual = BarkNormalizer().normalize(self.df, **self.kwargs)
#         self.assertTrue(actual.equals(expected))

#     @repeat_test()
#     def test_erb_normalizer(self):
#         """Test ErbNormalizer."""
#         expected = make_new_columns_expected(self.df, self.suffix, hz_to_erb)
#         actual = ErbNormalizer().normalize(self.df, **self.kwargs)
#         self.assertTrue(actual.equals(expected))

#     @repeat_test()
#     def test_log10_normalizer(self):
#         """Test Log10Normalizer."""
#         expected = make_new_columns_expected(self.df, self.suffix, np.log10)
#         actual = Log10Normalizer().normalize(self.df, **self.kwargs)
#         self.assertTrue(actual.equals(expected))

#     @repeat_test()
#     def test_log_normalizer(self):
#         """Test LogNormalizer."""
#         expected = make_new_columns_expected(self.df, self.suffix, np.log)
#         actual = LogNormalizer().normalize(self.df, **self.kwargs)
#         self.assertTrue(actual.equals(expected))

#     @repeat_test()
#     def test_mel_normalizer(self):
#         """Test MelNormalizer."""
#         expected = make_new_columns_expected(self.df, self.suffix, hz_to_mel)
#         actual = MelNormalizer().normalize(self.df, **self.kwargs)
#         self.assertTrue(actual.equals(expected))


