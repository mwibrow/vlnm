"""
Helpers for tests.
"""
import itertools
import unittest

import numpy as np
import pandas as pd
import pandas.testing

from vlnm.normalizers.base import Normalizer

# There are issues wth pandas and pylint
# See https://github.com/PyCQA/pylint/issues/2198 for some discussion.
#
#
DataFrame = pd.DataFrame
Series = pd.Series

def assert_frame_equal(*args, **kwargs):
    """Wrapper around pandas testing helper"""
    return pandas.testing.assert_frame_equal(*args, **kwargs)

def assert_series_equal(*args, **kwargs):
    """Wrapper around pandas testing helper"""
    return pandas.testing.assert_series_equal(*args, **kwargs)

def concat_df(*args, **kwargs):
    """Wrapper around pandas data-frame conact"""
    return pd.concat(*args, **kwargs)

def make_set_up(set_up=None):
    """Make the set up function for a repeating test."""
    def _do_set_up(obj):
        if set_up:
            return set_up(obj)
        return obj.setUp()
    return _do_set_up

def repeat_test(iterations=1, seed=None, set_up=None):
    """
    Decorator for repeating tests with random numbers.
    """
    set_up = make_set_up(set_up=set_up)
    def _decorator(method):
        def _wrapper(self, *args, **kwargs):
            np.random.seed(seed)
            for _ in range(iterations):
                set_up(self)
                method(self, *args, **kwargs)
        _wrapper.__name__ = method.__name__
        return _wrapper
    return _decorator


def generate_data_frame(
        speakers=1,
        genders=None,
        factors=None,
        na_percentage=1.):
    """
    Generate a random(ish) data-frame for testing.
    """
    df_factors = factors.copy()
    df_factors.update(speaker=[speaker for speaker in range(speakers)])
    base_df = pd.DataFrame(
        list(itertools.product(*df_factors.values())),
        columns=df_factors.keys())
    index = base_df['speaker'] % len(genders)
    base_df['gender'] = np.array(genders)[index]
    formants = ['f0', 'f1', 'f2', 'f3']
    for f, formant in enumerate(formants):
        base_df[formant] = (index + 1) * 250 + f * 400
        base_df[formant] += np.random.randint(50, size=len(base_df)) - 25
        i = np.random.random(len(base_df)) > (1. - na_percentage / 100.)
        base_df.loc[i, formant] = np.nan
    return base_df

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

# Fixed dataframe for each test run, if required.
DATA_FRAME = get_test_dataframe()


class Helper:
    """Wraper class for base test class."""


    class TestNormalizerBase(unittest.TestCase):
        """Common tests for the speaker normalizers."""

        normalizer = Normalizer

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.normalizer = self.__class__.normalizer

        def setUp(self):
            self.df = DATA_FRAME.copy()
            self.formants = ['f0', 'f1', 'f2', 'f3']
            self.kwargs = dict(formants=self.formants)

        def test_column_missing(self):
            """
            Missing speaker column raises ValueError.
            """
            for column in self.normalizer.required_columns:
                df = self.df.copy()
                df = df.drop(column, axis=1)
                with self.assertRaises(ValueError):
                    self.normalizer().normalize(df, **self.kwargs)

        def test_default_columns(self):
            """Check default columns returned."""
            expected = self.df.columns
            actual = self.normalizer().normalize(
                self.df, **self.kwargs).columns

            expected = sorted(expected)
            actual = sorted(actual)
            self.assertListEqual(actual, expected)

        def test_new_columns(self):
            """Check new columns returned."""
            rename = '{}\''
            expected = (list(self.df.columns) +
                        list(rename.format(f) for f in self.formants))
            actual = self.normalizer().normalize(
                self.df, rename=rename, **self.kwargs).columns

            expected = sorted(expected)
            actual = sorted(actual)
            self.assertListEqual(actual, expected)


    class TestFormantNormalizerBase(TestNormalizerBase):
        """Common tests for the formant normalizers."""

        transform = lambda x: x

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.transform = self.__class__.transform

        def test_normalize(self):
            """Test normalize output."""
            expected = self.df.copy()
            expected[self.formants] = self.transform(expected[self.formants])
            actual = self.normalizer().normalize(self.df, **self.kwargs)
            assert_frame_equal(actual, expected)


    class SpeakerNormalizerTests(TestNormalizerBase):
        """Common tests for the speaker normalizers."""

        def test_incorrect_alias(self):
            """
            Missing aliased column raises ValueError.
            """
            df = self.df.copy()
            with self.assertRaises(ValueError):
                self.normalizer().normalize(
                    df, speaker='talker', **self.kwargs)
