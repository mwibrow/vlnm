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
    BarkDifferenceNormalizer,
    BladenNormalizer,
    ErbNormalizer,
    Log10Normalizer,
    LogNormalizer,
    MelNormalizer
)


DATA_FRAME = pd.DataFrame(dict(
    gender=['M'] * 4 + ['F'] * 4,
    f0=[100 + i * 50 for i in range(8)],
    f1=[500 + i * 50 for i in range(8)],
    f2=[1000 + i * 50 for i in range(8)],
    f3=[2000 + i * 50 for i in range(8)]
))

class TestIntrinsicNormalizersValueError(unittest.TestCase):
    """
    Check normalizers raise ValueError if no formants specified.
    """

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        with self.assertRaises(ValueError):
            BarkNormalizer().normalize(DATA_FRAME)

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        with self.assertRaises(ValueError):
            ErbNormalizer().normalize(DATA_FRAME)

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        with self.assertRaises(ValueError):
            Log10Normalizer().normalize(DATA_FRAME)

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        with self.assertRaises(ValueError):
            LogNormalizer().normalize(DATA_FRAME)

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        with self.assertRaises(ValueError):
            MelNormalizer().normalize(DATA_FRAME)


class TestIntrinsicNormalizersSunnyDay(unittest.TestCase):
    """
    Sunny day tests for normalizers
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()[['f0', 'f1', 'f2', 'f3']]
        self.kwargs = dict(formants=['f0', 'f1', 'f2', 'f3'])

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        expected = hz_to_bark(self.df.copy())
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        expected = hz_to_erb(self.df.copy())
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        expected = np.log10(self.df.copy())
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        expected = np.log(self.df.copy())
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        expected = hz_to_mel(self.df.copy())
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))



def make_new_columns_expected(df, suffix, transform):
    """Helper for class Test new columns"""
    tmp_df = transform(df.copy())
    tmp_df.columns = ['{}{}'.format(column, suffix) for column in tmp_df.columns]
    return pd.concat([df.copy(), tmp_df], axis=1)

class TestIntrinsicNormalizersNewColumns(unittest.TestCase):
    """
    Test normalized formants as new columns.
    """

    def setUp(self):
        self.suffix = '_N'
        self.df = DATA_FRAME.copy()[['f0', 'f1', 'f2', 'f3']]
        self.kwargs = dict(
            formants=['f0', 'f1', 'f2', 'f3'],
            suffix=self.suffix)

    def test_bark_normalizer(self):
        """Test BarkNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_bark)
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_erb)
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, np.log10)
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, np.log)
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer"""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_mel)
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))


class TestBladenNormalizer(unittest.TestCase):
    """
    Test the BladenNormalizer
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(
            formants=self.formants)

    def test_no_gender(self):
        """No gender column raises ValueError"""
        with self.assertRaises(ValueError):
            BladenNormalizer().normalize(self.df, **self.kwargs)

    def test_no_male_or_female(self):
        """No female or male column raises ValueError"""
        with self.assertRaises(ValueError):
            BladenNormalizer().normalize(self.df, gender='gender', **self.kwargs)

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


class TestBarkDifferenceNormalizer(unittest.TestCase):
    """
    Test the BarkDifferenceNormalizer class
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_no_f0_or_f1(self):
        """No f0 or f1 columns ValueError"""
        with self.assertRaises(ValueError):
            BarkDifferenceNormalizer().normalize(self.df, **self.kwargs)

    def test_f0(self):
        """F0 subtraction"""
        expected = (hz_to_bark(self.df[self.formants]) -
            hz_to_bark(self.df['f0']))
        actual = BarkDifferenceNormalizer().normalize(
            self.df, f0='f0', **self.kwargs)
        self.assertTrue(actual[self.formants].equals(expected))
