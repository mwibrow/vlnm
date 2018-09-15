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
    BarkDifferenceNormalizer,
    BarkNormalizer,
    BladenNormalizer,
    ErbNormalizer,
    LogNormalizer,
    Log10Normalizer,
    MelNormalizer)
from vlnm.validation import (
    ChoiceKeywordMissingError
)
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



def rename_columns(df, rename, transform):
    """Helper for class Test new columns."""
    tmp_df = transform(df.copy())
    tmp_df.columns = [rename.format(column) for column in tmp_df.columns]
    return pd.concat([df.copy(), tmp_df], axis=1)

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

    @repeat_test()
    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_bark)
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_erb)
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = rename_columns(
            self.df, self.rename, np.log10)
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = rename_columns(self.df, self.rename, np.log)
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = rename_columns(
            self.df, self.rename, hz_to_mel)
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))


class TestBarkDifferenceNormalizer(unittest.TestCase):
    """
    Test the BarkDifferenceNormalizer class
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_formants(self):
        """Should normalize df."""
        expected = self.df.copy()
        expected['z1-z0'] = (
            hz_to_bark(self.df['f1']) - hz_to_bark(self.df['f0']))
        expected['z2-z1'] = (
            hz_to_bark(self.df['f2']) - hz_to_bark(self.df['f2']))
        expected['z3-z2'] = (
            hz_to_bark(self.df['f3']) - hz_to_bark(self.df['f2']))
        actual = BarkDifferenceNormalizer().normalize(
            self.df, f0='f0', **self.kwargs)
        self.assertTrue(actual[self.formants].equals(expected[self.formants]))


class TestBladenNormalizer(unittest.TestCase):
    """
    Test the BladenNormalizer.
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(
            formants=self.formants)

    def test_no_gender(self):
        """No gender column raises ValueError."""
        with self.assertRaises(ChoiceKeywordMissingError):
            BladenNormalizer().normalize(self.df, **self.kwargs)

    def test_no_male_or_female(self):
        """No female or male column raises ValueError."""
        with self.assertRaises(ChoiceKeywordMissingError):
            BladenNormalizer().normalize(
                self.df, gender='gender', **self.kwargs)

    def test_minimal_kwargs(self):
        """Minimally correct kwargs."""
        BladenNormalizer().normalize(
            self.df,
            gender='gender', male='M', **self.kwargs)

    def test_with_female(self):
        """Test specifying female label."""
        normalizer = BladenNormalizer()

        expected = hz_to_bark(self.df.copy()[self.formants])
        expected[self.df['gender'] == 'F'] -= 1.
        actual = normalizer.normalize(
            self.df,
            gender='gender',
            female='F',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))

    def test_with_male(self):
        """Test specifying male label."""
        normalizer = BladenNormalizer()
        expected = hz_to_bark(self.df.copy()[self.formants])
        expected[self.df['gender'] == 'F'] -= 1.
        actual = normalizer.normalize(
            self.df,
            gender='gender',
            male='M',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))
