"""
Tests for 'centroid' normalizers
"""

import unittest

import pandas as pd

from vlnm.normalizers import (
    BighamNormalizer,
    VowelNormalizer,
    SchwaNormalizer,
    WattFabriciusNormalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer)
from vlnm.validation import (
    RequiredColumnMissingError,
    RequiredColumnAliasMissingError,
    RequiredKeywordMissingError)
from tests.helpers import (
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


class BaseTestCases:  # pylint: disable=too-few-public-methods
    """
    Wrapper around command test cases.
    """

    class TestCentroidNormalizer(unittest.TestCase):
        """
        Base class for 'centroid' normalizer classes
        """

        normalizer = VowelNormalizer
        required_kwargs = {}

        def __init__(self, *args, **kwargs):
            super(BaseTestCases.TestCentroidNormalizer, self).__init__(
                *args, **kwargs)
            self.normalizer = self.__class__.normalizer

        def setUp(self):
            self.df = get_test_dataframe()
            self.formants = ['f0', 'f1', 'f2', 'f3']
            self.kwargs = dict(formants=self.formants)

        def test_missing_required_columns(self):
            """Missing required columns raises error."""
            normalizer = self.normalizer()
            for column in normalizer.get_columns().required:
                df = self.df.copy().drop(column, axis=1)
                with self.assertRaises(RequiredColumnMissingError):
                    normalizer.normalize(df, **self.kwargs)

        def test_missing_aliased_columns(self):
            """Missing aliased speaker column raises error."""
            normalizer = self.normalizer()
            for column in normalizer.get_columns().required:
                df = self.df.copy()
                alias = '{}_alias'.format(column)
                df = df.drop(column, axis=1)

                kwargs = {}
                kwargs.update(**self.kwargs)
                kwargs[column] = alias

                with self.assertRaises(RequiredColumnAliasMissingError):
                    normalizer.normalize(
                        df,
                        **kwargs)

        def test_missing_keywords(self):
            """Missing keywords raises error."""
            normalizer = self.normalizer()
            keywords = normalizer.get_keywords().required
            for keyword in keywords:
                df = self.df.copy()
                kwargs = {}
                kwargs.update(**self.kwargs)
                for word in keywords:
                    if word != keyword:
                        kwargs[keyword] = keyword

                with self.assertRaises(RequiredKeywordMissingError):
                    normalizer.normalize(
                        df,
                        **kwargs)

        def test_default_columns(self):
            """Check default columns returned."""
            expected = self.df.columns
            kwargs = {}
            kwargs.update(self.kwargs)
            kwargs.update(self.required_kwargs or {})
            actual = self.normalizer().normalize(
                self.df,
                **kwargs).columns

            expected = sorted(expected)
            actual = sorted(actual)
            self.assertListEqual(actual, expected)

        def test_new_columns(self):
            """Check new columns returned."""
            rename = '{}\''
            expected = (list(self.df.columns) +
                        list(rename.format(f) for f in self.formants))
            kwargs = {}
            kwargs.update(self.kwargs)
            kwargs.update(self.required_kwargs or {})
            actual = self.normalizer().normalize(
                self.df,
                rename=rename,
                **kwargs).columns

            expected = sorted(expected)
            actual = sorted(actual)
            self.assertListEqual(actual, expected)

class TestWattFabriciusNormalizer(BaseTestCases.TestCentroidNormalizer):
    """Tests for the WattFabriciusNormalizer Class. """

    normalizer = WattFabriciusNormalizer
    required_kwargs = dict(
        fleece='i',
        trap='a')

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.kwargs = dict(formants=self.formants)

    def test_speaker_stats(self):
        """Check speaker parameter values for all speakers."""
        df = pd.DataFrame(dict(
            speaker=['s1', 's1'],
            vowel=['fleece', 'trap'],
            f1=[100., 250.],
            f2=[400., 450.]
        ))
        constants = {}
        formants = ['f1', 'f2']
        WattFabriciusNormalizer.speaker_stats(
            df,
            formants=formants,
            fleece='fleece',
            trap='trap',
            constants=constants)

        expected = dict(
            f1_fleece=100.,
            f2_fleece=400.,
            f1_trap=250.,
            f2_trap=450.,
            f1_goose=100.,
            f2_goose=100.,
            f1_centroid=(100 + 250 + 100) / 3,
            f2_centroid=(400 + 450 + 100) / 3)

        self.assertDictEqual(
            constants,
            expected)




class TestWattFabricius2Normalizer(BaseTestCases.TestCentroidNormalizer):
    """Tests for the WattFabricius2Normalizer Class. """

    normalizer = WattFabricius2Normalizer
    required_kwargs = dict(
        fleece='i',
        trap='a')

    def test_speaker_stats(self):
        """Check speaker parameter values for all speakers."""
        df = pd.DataFrame(dict(
            speaker=['s1', 's1'],
            vowel=['fleece', 'trap'],
            f1=[100., 250.],
            f2=[400., 450.]
        ))
        constants = {}
        formants = ['f1', 'f2']
        WattFabricius2Normalizer.speaker_stats(
            df,
            formants=formants,
            fleece='fleece',
            trap='trap',
            constants=constants)

        expected = dict(
            f1_fleece=100.,
            f2_fleece=400.,
            f1_trap=250.,
            f2_trap=450.,
            f1_goose=100.,
            f2_goose=100.,
            f1_centroid=(100 + 250 + 100) / 3,
            f2_centroid=(400 + 100) / 2)

        self.assertDictEqual(
            constants,
            expected)


class TestWattFabricius3Normalizer(BaseTestCases.TestCentroidNormalizer):
    """Tests for the WattFabricius3Normalizer Class. """

    normalizer = WattFabricius3Normalizer
    required_kwargs = dict(
        fleece='i',
        trap='a',
        point_vowels=['i', 'a'])

    def test_speaker_stats(self):
        """Check speaker parameter values for all speakers."""
        df = pd.DataFrame(dict(
            speaker=['s1', 's1', 's1'],
            vowel=['fleece', 'trap', 'bath'],
            f1=[100., 250., 50.],
            f2=[400., 450., 300.]
        ))
        constants = {}
        formants = ['f1', 'f2']
        WattFabricius3Normalizer.speaker_stats(
            df,
            formants=formants,
            fleece='fleece',
            trap='trap',
            point_vowels=['fleece', 'trap', 'bath'],
            constants=constants)

        expected = dict(
            f1_fleece=100.,
            f2_fleece=400.,
            f1_trap=250.,
            f2_trap=450.,
            f1_goose=50.,
            f2_goose=300.,
            f1_centroid=(100 + 250 + 50) / 3,
            f2_centroid=(400 + 300) / 2)

        self.assertDictEqual(
            constants,
            expected)


class TestBighamNormalizer(BaseTestCases.TestCentroidNormalizer):
    """Tests for the BighamNormalizer Class. """

    normalizer = BighamNormalizer
    required_kwargs = dict(
        apices=['a', 'i', 'o', 'u'])

    def test_speaker_stats(self):
        """Check speaker parameter values for all speakers."""
        apices = ['a', 'i', 'o', 'u']
        df = self.df.copy()
        for speaker in df['speaker'].unique():
            speaker_df = df[df['speaker'] == speaker]

            actual = {}
            expected = {}
            for formant in self.formants:
                for apice in apices:
                    apice_df = speaker_df[speaker_df['vowel'] == apice]
                    expected['{}_{}'.format(formant, apice)] = (
                        apice_df[formant].mean())

                expected['{}_centroid'.format(formant)] = (
                    sum(expected['{}_{}'.format(formant, apice)]
                        for apice in apices) / len(apices))

            BighamNormalizer.speaker_stats(
                speaker_df,
                constants=actual,
                apices=apices,
                **self.kwargs)

            self.assertDictEqual(actual, expected)


class TestSchwaNormalizer(BaseTestCases.TestCentroidNormalizer):
    """Tests for the SchwaNormalizer Class. """

    normalizer = SchwaNormalizer
    required_kwargs = dict(
        schwa='e')

    def test_speaker_stats(self):
        """Check speaker parameter values for all speakers."""
        schwa = 'e'
        df = self.df.copy()
        for speaker in df['speaker'].unique():
            speaker_df = df[df['speaker'] == speaker]

            actual = {}
            expected = {}
            for formant in self.formants:
                expected['{}_centroid'.format(formant)] = (
                    speaker_df[speaker_df['vowel'] == schwa][formant].mean())

            SchwaNormalizer.speaker_stats(
                speaker_df,
                constants=actual,
                schwa=schwa,
                **self.kwargs)

            self.assertDictEqual(actual, expected)
