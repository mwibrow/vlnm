"""
Tests for 'centroid' normalizers
"""

import unittest

from vlnm.normalizers.centroid import (
    get_apice_formants,
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

class TestGetApiceFormants(unittest.TestCase):
    """Tests for the get_apice_formants function."""

    def test_output(self):
        """Simple output is correct."""
        df = DataFrame(dict(
            vowel=['fleece', 'fleece', 'trap', 'trap'],
            f1=[300., 350., 400., 450.],
            f2=[500., 550., 600., 650.]
        ))
        expected = DataFrame(dict(
            f1=[325., 425.],
            f2=[525., 625.]
        ), index=['fleece', 'trap'])
        expected.index.name = 'vowel'
        actual = get_apice_formants(
            df, dict(fleece='fleece', trap='trap'), 'vowel', ['f1', 'f2'])
        self.assertIsNone(assert_frame_equal(actual, expected))

    def test_apice_spec(self):
        """Non-defualt apices processed correctly."""
        df = DataFrame(dict(
            hvd=['heed', 'heed', 'had', 'had'],
            f1=[300., 350., 400., 450.],
            f2=[500., 550., 600., 650.]
        ))
        expected = DataFrame(dict(
            f1=[325., 425.],
            f2=[525., 625.]
        ), index=['fleece', 'trap'])
        expected.index.name = 'hvd'
        actual = get_apice_formants(
            df, dict(fleece='heed', trap='had'), 'hvd', ['f1', 'f2'])
        self.assertIsNone(assert_frame_equal(actual, expected))


class TestWattFabriciusNormalizer(Helper.SpeakerNormalizerTests):
    """Tests for the WattFabriciusNormalizer Class. """

    normalizer = WattFabriciusNormalizer

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.normalizer = self.__class__.normalizer
        self.kwargs = dict(
            formants=self.formants,
            fleece='i',
            trap='a',
            apices=['i', 'a'])

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
            fleece='fleece', trap='trap', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250. + 150.) / 3,
                f2=(450. + 550. + 150.) / 3),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)

    def test_default_keywords(self):
        """Check default keywords assigned."""
        df = self.df.copy()
        df.loc[df['vowel'] == 'i', 'vowel'] = 'fleece'
        df.loc[df['vowel'] == 'a', 'vowel'] = 'trap'
        normalizer = self.normalizer()
        normalizer.normalize(df)
        expected = dict(
            fleece='fleece',
            trap='trap')
        actual = {key: normalizer.options[key] for key in expected}
        self.assertDictEqual(actual, expected)


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
            fleece='fleece', trap='trap', vowel='vowel', formants=['f1', 'f2'])

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


class TestBighamNormalizer(TestWattFabriciusNormalizer):
    """Tests for the BighamNormalizer Class. """

    normalizer = BighamNormalizer

    def test_get_centroid(self):
        """Test the get_centroid method."""

        df = DataFrame(dict(
            speaker=['s1', 's1', 's1', 's1', 's1', 's1'],
            vowel=['fleece', 'fleece', 'trap', 'trap', 'kit', 'kit'],
            f1=[100., 200., 200., 300., 0., 100.],
            f2=[400., 500., 500., 600., 300., 400.]
        ))

        actual = self.normalizer.get_centroid(
            df, ['fleece', 'trap'],
            fleece='fleece', trap='trap', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250.) / 2,
                f2=(450. + 550.) / 2),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)

    def test_default_keywords(self):
        """Check default keywords assigned."""
        df = self.df.copy()
        df.loc[df['vowel'] == 'i', 'vowel'] = 'fleece'
        df.loc[df['vowel'] == 'a', 'vowel'] = 'trap'
        normalizer = self.normalizer()
        normalizer.normalize(df)
        expected = dict(
            apices=list(df['vowel'].unique()))
        actual = {key: normalizer.options[key] for key in expected}
        self.assertDictEqual(actual, expected)

class TestSchwaNormalizer(Helper.SpeakerNormalizerTests):
    """Tests for the SchwaNormalizer Class. """

    normalizer = SchwaNormalizer

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.normalizer = self.__class__.normalizer
        self.kwargs = dict(
            formants=self.formants,
            schwa='e')

    def test_get_centroid(self):
        """Test the get_centroid method."""
        df = DataFrame(dict(
            speaker=['s1', 's1'],
            vowel=['e', 'e'],
            f1=[100., 200.],
            f2=[400., 500.]
        ))
        actual = self.normalizer.get_centroid(
            df, ['e'], vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(100. + 200.) / 2,
                f2=(400. + 500.) / 2),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)
