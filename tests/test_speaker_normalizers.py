"""
Tests for the normalize module.
"""

# pylint: disable=protected-access

import unittest

import numpy as np

from vlnm.normalizers.speaker import (
    GerstmanNormalizer,
    LCENormalizer,
    LobanovNormalizer,
    NearyNormalizer,
    NearyGMNormalizer)

from tests.helpers import (
    assert_frame_equal,
    assert_series_equal,
    generate_data_frame)


def get_test_dataframe(speakers=2):
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

class TestLCENormalizer(unittest.TestCase):
    """
    Tests for the LCENormalizer class.
    """

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

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
        self.assertEqual(len(actual), len(expected))

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
    f_max = df[in_cols].max(axis=0)
    df[out_cols] = df[in_cols] / f_max
    return df


class TestGerstmanNormalizer(unittest.TestCase):
    """Tests for the GerstmanNormalizer class."""

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_output(self):
        """Check output."""
        df = GerstmanNormalizer().normalize(
            self.df.copy(),
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                fmin = expected_df[formant].min(axis=0)
                fmax = expected_df[formant].max(axis=0)

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


class TestLobanovNormalizer(unittest.TestCase):
    """Tests for the LobanovNormalizer class."""

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_output(self):
        """Check output."""
        df = LobanovNormalizer().normalize(
            self.df.copy(),
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                mu = expected_df[formant].mean()
                sigma = expected_df[formant].std() or 0.

                actual = actual_df[formant]
                expected = (expected_df[formant] - mu) / sigma if sigma else 0.

                assert_series_equal(actual, expected)

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = LobanovNormalizer().normalize(
            self.df, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
                    list(rename.format(f) for f in self.formants))
        actual = LobanovNormalizer().normalize(
            self.df, rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)


class TestNearyNormalizer(unittest.TestCase):
    """Tests for the NearyNormalizer class."""

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_output(self):
        """Check output."""
        df = NearyNormalizer().normalize(
            self.df.copy(),
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                mu_log = np.log(expected_df[formant]).mean(axis=0)

                actual = actual_df[formant]
                expected = np.log(expected_df[formant]) - mu_log

                assert_series_equal(actual, expected)

    def test_output_transform(self):
        """Check output with exponential transform."""
        df = NearyNormalizer().normalize(
            self.df.copy(),
            transform=True,
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                mu_log = np.log(expected_df[formant]).mean(axis=0)

                actual = actual_df[formant]
                expected = np.exp(
                    np.log(expected_df[formant]) - mu_log)

                assert_series_equal(actual, expected)

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = NearyNormalizer().normalize(
            self.df, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
                    list(rename.format(f) for f in self.formants))
        actual = NearyNormalizer().normalize(
            self.df, rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)


class TestNearyGMNormalizer(unittest.TestCase):
    """Tests for the NearyGMNormalizer Class. """

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_output(self):
        """Check output for extrinsic normalizer."""
        df = NearyGMNormalizer().normalize(
            self.df.copy(),
            method='extrinsic',
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                mu_log = np.log(
                    expected_df[self.formants]).mean(axis=0).mean()

                actual = actual_df[formant]
                expected = np.log(expected_df[formant]) - mu_log

                assert_series_equal(actual, expected)

    def test_output_transform(self):
        """Check output for extrinsic normalizer with exponential transform."""
        df = NearyGMNormalizer().normalize(
            self.df.copy(),
            method='extrinsic',
            transform=True,
            **self.kwargs)

        self.assertEqual(len(df), len(self.df))

        for speaker in self.df['speaker'].unique():
            actual_df = df[df['speaker'] == speaker]
            expected_df = self.df[self.df['speaker'] == speaker]
            for formant in self.formants:
                mu_log = np.log(
                    expected_df[self.formants]).mean(axis=0).mean()

                actual = actual_df[formant]
                expected = np.exp(
                    np.log(expected_df[formant]) - mu_log)

                assert_series_equal(actual, expected)

    def test_default_columns(self):
        """Check default columns returned."""
        expected = self.df.columns
        actual = NearyGMNormalizer().normalize(
            self.df, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}\''
        expected = (list(self.df.columns) +
                    list(rename.format(f) for f in self.formants))
        actual = NearyGMNormalizer().normalize(
            self.df, rename=rename, **self.kwargs).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)
