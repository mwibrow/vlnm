"""
Tests for the normalizers library.
"""
import itertools
import unittest

import numpy as np
from numpy.random import seed as random_seed
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
    MelNormalizer,
    NordstromNormalizer
)

def generate_data_frame(
        speakers=1,
        genders=None,
        factors=None,
        seed=None):
    """
    Generate a random(ish) data-frame for testing.
    """
    random_seed(seed)
    df_factors = factors.copy()
    df_factors.update(speaker=[speaker for speaker in range(speakers)])
    base_df = pd.DataFrame(list(itertools.product(*df_factors.values())),
        columns=df_factors.keys())
    index = base_df['speaker'] % len(genders)
    base_df['gender'] = np.array(genders)[index]
    formants = ['f0', 'f1', 'f2', 'f3']
    for f, formant in enumerate(formants):
        base_df[formant] = (index + 1) * 250 + f * 400
        base_df[formant] += np.random.randint(50, size=len(base_df)) - 25
    return base_df


DATA_FRAME = generate_data_frame(
    speakers = 8,
    genders=['M', 'F'],
    factors=dict(
        group=['HV', 'LV'],
        test=['pre', 'post'],
        vowel=['a', 'e', 'i', 'o', 'u']))

class TestIntrinsicNormalizersValueError(unittest.TestCase):
    """
    Check normalizers raise ValueError if no formants specified.
    """

    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        with self.assertRaises(ValueError):
            BarkNormalizer().normalize(DATA_FRAME)

    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        with self.assertRaises(ValueError):
            ErbNormalizer().normalize(DATA_FRAME)

    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        with self.assertRaises(ValueError):
            Log10Normalizer().normalize(DATA_FRAME)

    def test_log_normalizer(self):
        """Test LogNormalizer."""
        with self.assertRaises(ValueError):
            LogNormalizer().normalize(DATA_FRAME)

    def test_mel_normalizer(self):
        """Test MelNormalizer."""
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



def make_new_columns_expected(df, suffix, transform):
    """Helper for class Test new columns."""
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
        """Test BarkNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_bark)
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_erb)
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, np.log10)
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, np.log)
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    def test_mel_normalizer(self):
        """Test MelNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_mel)
        actual = MelNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))


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
        with self.assertRaises(ValueError):
            BladenNormalizer().normalize(self.df, **self.kwargs)

    def test_no_male_or_female(self):
        """No female or male column raises ValueError."""
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
        """No f0 or f1 columns ValueError."""
        with self.assertRaises(ValueError):
            BarkDifferenceNormalizer().normalize(self.df, **self.kwargs)

    def test_f0(self):
        """F0 subtraction."""
        expected = self.df.copy()
        for formant in self.formants:
            expected[formant] = (hz_to_bark(self.df[formant]) -
                                 hz_to_bark(self.df['f0']))
        actual = BarkDifferenceNormalizer().normalize(
            self.df, f0='f0', **self.kwargs)
        self.assertTrue(actual[self.formants].equals(expected[self.formants]))

    def test_f1(self):
        """F1 subtraction."""
        expected = self.df.copy()
        for formant in self.formants:
            expected[formant] = (hz_to_bark(self.df[formant]) -
                                 hz_to_bark(self.df['f1']))
        actual = BarkDifferenceNormalizer().normalize(
            self.df, f1='f1', **self.kwargs)
        self.assertTrue(actual[self.formants].equals(expected[self.formants]))


class TestNordstromNormalizer(unittest.TestCase):
    """
    Tests for the NordstromNormalizer class.
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict(
            formants=self.formants)

    def test_no_f1_or_f3(self):
        """No f1 or f3 columns ValueError."""
        with self.assertRaises(ValueError):
            NordstromNormalizer().normalize(self.df, formants=[])

    def test_mu_ratio(self):
        """Calculate mu ratios."""
        df = self.df
        mu_male = df[(df['gender'] == 'M') & (df['f1'] > 600)]['f3'].mean()
        mu_female = df[(df['gender'] == 'F') & (df['f1'] > 600)]['f3'].mean()

        constants = {}
        NordstromNormalizer().calculate_f3_means(
            df,
            f1='f1',
            f3='f3',
            constants=constants,
            gender='gender',
            female='F')
        self.assertEqual(constants['mu_female'], mu_female)
        self.assertEqual(constants['mu_male'], mu_male)
