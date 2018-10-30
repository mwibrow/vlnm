"""
Tests for 'centroid' normalizers
"""

import pandas as pd

from vlnm.normalizers.centroid import (
    BighamNormalizer,
    SchwaNormalizer,
    WattFabriciusNormalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer)
from tests.helpers import (
    get_test_dataframe,
    BaseTestCases)


class TestWattFabriciusNormalizer(BaseTestCases.BaseTestNormalizer):
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




class TestWattFabricius2Normalizer(BaseTestCases.BaseTestNormalizer):
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


class TestWattFabricius3Normalizer(BaseTestCases.BaseTestNormalizer):
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


class TestBighamNormalizer(BaseTestCases.BaseTestNormalizer):
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


class TestSchwaNormalizer(BaseTestCases.BaseTestNormalizer):
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
