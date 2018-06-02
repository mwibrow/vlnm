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
    GerstmanNormalizer,
    LobanovNormalizer,
    Log10Normalizer,
    LogNormalizer,
    LCENormalizer,
    MelNormalizer,
    NearyNormalizer,
    NordstromNormalizer
)

from tests.helpers import (
    generate_data_frame,
    repeat_test)


def get_test_dataframe():
    """Generate a test dataframe."""
    df = generate_data_frame(
        speakers=8,
        genders=['M', 'F'],
        factors=dict(
            group=['HV', 'LV'],
            test=['pre', 'post'],
            vowel=['a', 'e', 'i', 'o', 'u']))
    return df


DATA_FRAME = get_test_dataframe()

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
            suffix=self.suffix)

    @repeat_test()
    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_bark)
        actual = BarkNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, hz_to_erb)
        actual = ErbNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, np.log10)
        actual = Log10Normalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = make_new_columns_expected(self.df, self.suffix, np.log)
        actual = LogNormalizer().normalize(self.df, **self.kwargs)
        self.assertTrue(actual.equals(expected))

    @repeat_test()
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


class TestLCENormalizer(unittest.TestCase):
    """
    Tests for the LCENormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.kwargs = dict(
            formants=['f1', 'f2', 'f3'])

    @repeat_test()
    def test_speaker_summary(self):
        """Check maximum formant value for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            cols_in = self.kwargs['formants']
            expected = {}
            for col in cols_in:
                expected['{}_max'.format(col)] = df[col].max()
            actual = {}
            LCENormalizer().speaker_summary(
                df,
                cols_in=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)


class TestGerstmanNormalizer(unittest.TestCase):
    """
    Tests for the GerstmanNormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.kwargs = dict(
            formants=['f1', 'f2', 'f3'])

    @repeat_test()
    def test_speaker_summary(self):
        """Check maximum and minium formant value for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            cols_in = self.kwargs['formants']
            expected = {}
            for col in cols_in:
                expected['{}_max'.format(col)] = df[col].max()
                expected['{}_min'.format(col)] = df[col].min()
            actual = {}
            GerstmanNormalizer().speaker_summary(
                df,
                cols_in=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)


class TestLobanovNormalizer(unittest.TestCase):
    """
    Tests for the LobanovNormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.kwargs = dict(
            formants=['f1', 'f2', 'f3'])

    @repeat_test()
    def test_speaker_summary(self):
        """Check mean and standard formant values for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            cols_in = self.kwargs['formants']
            expected = {}
            for col in cols_in:
                expected['{}_mu'.format(col)] = df[col].mean()
                expected['{}_sigma'.format(col)] = df[col].std()
            actual = {}
            LobanovNormalizer().speaker_summary(
                df,
                cols_in=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)


class TestNearyNormalizer(unittest.TestCase):
    """
    Tests for the NearyNormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.kwargs = dict(
            formants=['f1', 'f2', 'f3'])

    @repeat_test()
    def test_speaker_summary(self):
        """Check mean log formant values for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            cols_in = self.kwargs['formants']
            expected = {}
            for col in cols_in:
                expected['{}_mu_log'.format(col)] = (
                    np.mean(np.log(df[col].dropna())))
            actual = {}
            NearyNormalizer().speaker_summary(
                df,
                cols_in=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)
