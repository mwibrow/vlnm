"""
Tests for 'centroid' normalizers
"""

from vlnm.normalizers.centroid import (
    BighamNormalizer,
    SchwaNormalizer,
    WattFabriciusNormalizer,
    WattFabricius2Normalizer,
    WattFabricius3Normalizer)
from tests.test_speaker_normalizers import Helper
from tests.helpers import (
    get_test_dataframe,
    assert_frame_equal,
    assert_series_equal,
    DataFrame,
    Series)


class TestWattFabriciusNormalizer(Helper.SpeakerNormalizerTests):
    """Tests for the WattFabriciusNormalizer Class. """

    normalizer = WattFabriciusNormalizer

    required_kwargs = dict(
        fleece='i',
        trap='a')

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.normalizer = self.__class__.normalizer
        self.kwargs = dict(
            formants=self.formants,
            fleece='i',
            trap='a',
            apices=['i', 'a'])

    def test_apice_formants(self):
        """Test the get_apice_formants method."""
        df = DataFrame(dict(
            speaker=['s1', 's1'],
            vowel=['fleece', 'trap'],
            f1=[100., 250.],
            f2=[400., 450.]
        ))
        actual = self.normalizer.get_apice_formants(
            df, ['fleece', 'trap'], vowel='vowel', formants=['f1', 'f2'])

        expected = DataFrame(dict(
            f1=df['f1'],
            f2=df['f2']))
        expected.index = ['fleece', 'trap']
        expected.index.name = 'vowel'
        assert_frame_equal(actual, expected)

    def test_get_centroid(self):
        """Test get_centroid method."""
        df = DataFrame(dict(
            speaker=['s1', 's1', 's1', 's1'],
            vowel=['fleece', 'fleece', 'trap', 'trap'],
            f1=[100., 200., 200., 300.],
            f2=[400., 500., 500., 600.]
        ))
        actual = self.normalizer.get_centroid(
            df, ['fleece', 'trap'],
            fleece='fleece', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250. + 150.) / 3,
                f2=(450. + 550. + 150.) / 3),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)


class TestWattFabricius2Normalizer(TestWattFabriciusNormalizer):
    """Tests for the WattFabricius2Normalizer Class. """

    normalizer = WattFabricius2Normalizer

    def test_get_centroid(self):
        """Test get_centroid method."""
        df = DataFrame(dict(
            speaker=['s1', 's1', 's1', 's1'],
            vowel=['fleece', 'fleece', 'trap', 'trap'],
            f1=[100., 200., 200., 300.],
            f2=[400., 500., 500., 600.]
        ))
        actual = self.normalizer.get_centroid(
            df, ['fleece', 'trap'],
            fleece='fleece', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250. + 150.) / 3,
                f2=(450. + 150.) / 2),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)


class TestWattFabricius3Normalizer(TestWattFabriciusNormalizer):
    """Tests for the WattFabricius3Normalizer Class. """

    normalizer = WattFabricius3Normalizer

    def test_get_centroid(self):
        """Test get_centroid method."""
        df = DataFrame(dict(
            speaker=['s1', 's1', 's1', 's1', 's1', 's1'],
            vowel=['fleece', 'fleece', 'trap', 'trap', 'kit', 'kit'],
            f1=[100., 200., 200., 300., 0., 100.],
            f2=[400., 500., 500., 600., 300., 400.]
        ))
        actual = self.normalizer.get_centroid(
            df, ['fleece', 'trap'],
            fleece='fleece', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250. + 50.) / 3,
                f2=(450. + 550. + 350.) / 3),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)


# class TestBighamNormalizer(unittest.TestCase):
#     """Tests for the BighamNormalizer Class. """

#     normalizer = BighamNormalizer
#     required_kwargs = dict(
#         apices=['a', 'i', 'o', 'u'])

#     def test_speaker_stats(self):
#         """Check speaker parameter values for all speakers."""
#         apices = ['a', 'i', 'o', 'u']
#         df = self.df.copy()
#         for speaker in df['speaker'].unique():
#             speaker_df = df[df['speaker'] == speaker]

#             actual = {}
#             expected = {}
#             for formant in self.formants:
#                 for apice in apices:
#                     apice_df = speaker_df[speaker_df['vowel'] == apice]
#                     expected['{}_{}'.format(formant, apice)] = (
#                         apice_df[formant].mean())

#                 expected['{}_centroid'.format(formant)] = (
#                     sum(expected['{}_{}'.format(formant, apice)]
#                         for apice in apices) / len(apices))

#             BighamNormalizer.speaker_stats(
#                 speaker_df,
#                 constants=actual,
#                 apices=apices,
#                 **self.kwargs)

#             self.assertDictEqual(actual, expected)


# class TestSchwaNormalizer(unittest.TestCase):
#     """Tests for the SchwaNormalizer Class. """

#     normalizer = SchwaNormalizer
#     required_kwargs = dict(
#         schwa='e')

#     def test_speaker_stats(self):
#         """Check speaker parameter values for all speakers."""
#         schwa = 'e'
#         df = self.df.copy()
#         for speaker in df['speaker'].unique():
#             speaker_df = df[df['speaker'] == speaker]

#             actual = {}
#             expected = {}
#             for formant in self.formants:
#                 expected['{}_centroid'.format(formant)] = (
#                     speaker_df[speaker_df['vowel'] == schwa][formant].mean())

#             SchwaNormalizer.speaker_stats(
#                 speaker_df,
#                 constants=actual,
#                 schwa=schwa,
#                 **self.kwargs)

#             self.assertDictEqual(actual, expected)
