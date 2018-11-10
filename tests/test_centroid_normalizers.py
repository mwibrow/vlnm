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
    assert_series_equal,
    DataFrame,
    Series)


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
            fleece='fleece', vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250.) / 2,
                f2=(450. + 550.) / 2),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)



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
