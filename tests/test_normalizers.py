"""
Tests for the normalize module.
"""

import unittest

import numpy as np
import pandas as pd
from pandas.testing import (
    assert_frame_equal,
    assert_series_equal)

from vlnm.conversion import (
    hz_to_bark,
    hz_to_erb,
    hz_to_mel)
from vlnm.normalizers import (
    BarkDifferenceNormalizer,
    BarkNormalizer,
    BladenNormalizer,
    ErbNormalizer,
    GerstmanNormalizer,
    LCENormalizer,
    LogNormalizer,
    Log10Normalizer,
    MelNormalizer,
    NordstromNormalizer)
from vlnm.validation import (
    ChoiceKeywordMissingError,
    RequiredColumnMissingError,
    RequiredColumnAliasMissingError
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

    @repeat_test()
    def test_bark_normalizer(self):
        """Test BarkNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = hz_to_bark(expected['f0@50'])
        actual = BarkNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_erb_normalizer(self):
        """Test ErbNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = hz_to_erb(expected['f0@50'])
        actual = ErbNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log10_normalizer(self):
        """Test Log10Normalizer."""
        expected = self.df.copy()
        expected['f0@50'] = np.log10(expected['f0@50'])
        actual = Log10Normalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    @repeat_test()
    def test_log_normalizer(self):
        """Test LogNormalizer."""
        expected = self.df.copy()
        expected['f0@50'] = np.log(expected['f0@50'])
        actual = LogNormalizer().normalize(self.df, f0='f0@50')
        self.assertTrue(actual.equals(expected))

    @repeat_test()
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

    def test_no_gender_alias(self):
        """No gender column alias raises ValueError."""
        with self.assertRaises(RequiredColumnAliasMissingError):
            df = self.df.copy()
            df = df.drop('gender', axis=1)
            BladenNormalizer().normalize(
                df,
                aliases=dict(gender='sex'),
                **self.kwargs)

    def test_no_male_or_female(self):
        """No female or male column raises Error."""
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

    def test_gender_alias(self):
        """Test aliased gender column."""
        normalizer = BladenNormalizer()

        df = self.df.copy()
        df['sex'] = df['gender']
        df = df.drop('gender', axis=1)

        expected = hz_to_bark(df[self.formants])
        expected[df['sex'] == 'F'] -= 1.
        actual = normalizer.normalize(
            df,
            aliases=dict(gender='sex'),
            female='F',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))

    def test_gender_alias_keyword(self):
        """Test keyword aliased gender column."""
        normalizer = BladenNormalizer()

        df = self.df.copy()
        df['sex'] = df['gender']
        df = df.drop('gender', axis=1)

        expected = hz_to_bark(df[self.formants])
        expected[df['sex'] == 'F'] -= 1.
        actual = normalizer.normalize(
            df,
            gender='sex',
            female='F',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = BladenNormalizer().normalize(
            self.df,
            gender='gender', male='M', **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
            list(rename.format(f) for f in self.formants))
        actual = BladenNormalizer().normalize(
            self.df,
            gender='gender', male='M', rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

class TestNordstromNormalizer(unittest.TestCase):
    """
    Tests for the NordstromNormalizer class.
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict(
            formants=self.formants)

    def test_no_gender_column(self):
        """No gender column."""
        with self.assertRaises(RequiredColumnMissingError):
            df = self.df.copy()
            df = df.drop('gender', axis=1)
            NordstromNormalizer().normalize(df, female='F')

    def test_no_aliased_gender_column(self):
        """No aliased gender column."""
        with self.assertRaises(RequiredColumnAliasMissingError):
            df = self.df.copy()
            NordstromNormalizer().normalize(
                df,
                female='F',
                aliases=dict(
                    gender='sex'
                ))

    def test_no_female_or_male_label(self):
        """No female or male label raise error."""
        with self.assertRaises(ChoiceKeywordMissingError):
            NordstromNormalizer().normalize(self.df)

    def test_mu_ratio(self):
        """Calculate mu ratios."""
        df = self.df
        mu_male = df[(df['gender'] == 'M') & (df['f1'] > 600)]['f3'].mean()
        mu_female = df[(df['gender'] == 'F') & (df['f1'] > 600)]['f3'].mean()

        constants = {}
        NordstromNormalizer().calculate_f3_means(
            df,
            constants=constants,
            gender='gender',
            female='F')
        self.assertEqual(constants['mu_female'], mu_female)
        self.assertEqual(constants['mu_male'], mu_male)

    def test_output(self):
        """Test output of Nordstrom normalizer."""
        df = self.df
        actual = NordstromNormalizer().normalize(
            df, gender='gender', female='F')
        self.assertTrue(actual is not None)

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = NordstromNormalizer().normalize(
            self.df,
            gender='gender', male='M', **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
            list(rename.format(f) for f in self.formants))
        actual = NordstromNormalizer().normalize(
            self.df,
            gender='gender', male='M', rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)


class TestLCENormalizer(unittest.TestCase):
    """
    Tests for the LCENormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    @repeat_test()
    def test_get_speaker_max(self):
        """Check maximum formant value for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            formants = self.kwargs['formants']
            expected = {}
            for formant in formants:
                expected['{}_max'.format(formant)] = df[formant].max()
            actual = {}
            LCENormalizer().get_speaker_max(
                df,
                formants=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)

    def test_no_constants(self):
        """No constants in norm method returns data frame."""
        df = True  # Actual value doesn't matter
        expected = df
        actual = LCENormalizer().norm(
            df, formants=['f0', 'f1', 'f2'], constants={})
        self.assertEqual(expected, actual)

    def test_no_formants(self):
        """No formants in norm method returns data frame."""
        df = True  # Actual value doesn't matter
        expected = df
        actual = LCENormalizer().norm(
            df, formants={}, constants=dict(mu=1.))
        self.assertEqual(expected, actual)

    @repeat_test()
    def test_output(self):
        """
        Check normalized formant output.
        """
        rename = '{}_N'
        df = self.df.copy()
        formants = self.kwargs['formants']
        expected = df.groupby('speaker', as_index=False).apply(
            lambda x: lce_helper(x, formants, rename))

        actual = LCENormalizer().normalize(
            self.df,
            rename='{}_N',
            speaker='speaker')

        expected = expected.dropna().sort_values(
            by=sorted(expected.columns)).reset_index(drop=True)
        actual = actual.dropna().sort_values(
            by=sorted(actual.columns)).reset_index(drop=True)

        try:
            assert_frame_equal(
                actual,
                expected,
                check_exact=False,
                check_less_precise=False)
        except AssertionError:
            for i in range(len(expected)):
                self.assertDictEqual(
                    actual.loc[i, :].to_dict(),
                    expected.loc[i, :].to_dict())

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = LCENormalizer().normalize(
            self.df, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
            list(rename.format(f) for f in self.formants))
        actual = LCENormalizer().normalize(
            self.df, rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)


def lce_helper(df, formants, rename):
    """Helper for LCENormalizerTests."""
    in_cols = formants
    out_cols = [rename.format(col) for col in in_cols]
    f_max = df[in_cols].max()
    df[out_cols] = df[in_cols] / f_max
    return df


class TestGerstmanNormalizer(unittest.TestCase):
    """Tests for the Gerstman normalizer class."""

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)


    @repeat_test()
    def test_speaker_summary(self):
        """Check maximum and minimum value for all speakers."""
        for speaker in self.df['speaker'].unique():
            df = self.df[self.df['speaker'] == speaker]
            formants = self.kwargs['formants']
            expected = {}
            for formant in formants:
                expected['{}_min'.format(formant)] = df[formant].min()
                expected['{}_max'.format(formant)] = df[formant].max()
            actual = {}
            GerstmanNormalizer().speaker_range(
                df,
                formants=self.kwargs['formants'],
                constants=actual)
            self.assertDictEqual(actual, expected)

    def test_no_speaker(self):
        """No speaker column raises error."""
        df = self.df.copy().drop('speaker', axis=1)
        with self.assertRaises(RequiredColumnMissingError):
            GerstmanNormalizer().normalize(df, **self.kwargs)

    def test_no_aliased_speaker(self):
        """No alised speaker column raises error."""

        df = self.df.copy()
        with self.assertRaises(RequiredColumnAliasMissingError):
            GerstmanNormalizer().normalize(
                df,
                speaker='participant',
                **self.kwargs)

    def test_output(self):
        """Check output."""
        df = GerstmanNormalizer().normalize(
            self.df.copy(),
            **self.kwargs)

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                fmin = expected_df[formant].min()
                fmax = expected_df[formant].max()

                actual = actual_df[formant]
                expected = 999 * (expected_df[formant] - fmin) / (fmax - fmin)

                assert_series_equal(actual, expected)

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = GerstmanNormalizer().normalize(
            self.df, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
            list(rename.format(f) for f in self.formants))
        actual = GerstmanNormalizer().normalize(
            self.df, rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)
