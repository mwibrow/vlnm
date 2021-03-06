"""
Tests for 'centroid' normalizers
"""

import unittest

from vlnm.normalizers.centroid import (
    _get_apice_formants,
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
        actual = _get_apice_formants(
            df, dict(fleece='fleece', trap='trap'), 'vowel', ['f1', 'f2'])
        self.assertIsNone(assert_frame_equal(actual, expected))

    def test_apice_spec(self):
        """Non-defualt points processed correctly."""
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
        actual = _get_apice_formants(
            df, dict(fleece='heed', trap='had'), 'hvd', ['f1', 'f2'])
        self.assertIsNone(assert_frame_equal(
            actual.sort_index(), expected.sort_index()))


class TestWattFabriciusNormalizer(Helper.SpeakerNormalizerTests):
    """Tests for the WattFabriciusNormalizer Class. """

    normalizer = WattFabriciusNormalizer

    def setUp(self):
        self.df = get_test_dataframe()
        self.formants = ['f0', 'f1', 'f2', 'f3']
        self.normalizer = self.__class__.normalizer
        self.kwargs = dict(
            formants=self.formants,
            points=dict(fleece='i', trap='a'))

    def test_new_columns(self):
        """Check new columns returned."""
        rename = '{}*'
        expected = (list(self.df.columns) +
                    list(rename.format(f) for f in ['f1', 'f2']))
        actual = self.normalizer(rename=rename, **self.kwargs).normalize(
            self.df).columns

        expected = sorted(expected)
        actual = sorted(actual)
        self.assertListEqual(actual, expected)

    def test_get_centroid(self):
        """Test get_centroid method."""
        df = DataFrame(dict(
            speaker=['s1', 's1', 's1', 's1'],
            vowel=['fleece', 'fleece', 'trap', 'trap'],
            f1=[100., 200., 200., 300.],
            f2=[400., 500., 500., 600.]
        ))
        actual = self.normalizer.get_centroid(
            df, dict(fleece='fleece', trap='trap'),
            vowel='vowel', formants=['f1', 'f2'])

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
            df, dict(fleece='fleece', trap='trap'),
            vowel='vowel', formants=['f1', 'f2'])

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
            df, dict(fleece='fleece', trap='trap'),
            formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(150. + 250. + 50.) / 3,
                f2=(450. + 550. + 350.) / 3),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)


class TestBighamNormalizer(TestWattFabriciusNormalizer):
    """Tests for the BighamNormalizer Class. """

    normalizer = BighamNormalizer

    def setUp(self):
        self.df = DataFrame(dict(
            speaker=['S1'] * 6 + ['S2'] * 6,
            vowel=['kit', 'goose', 'fleece', 'start', 'thought', 'trap'] * 2,
            f1=[200., 210., 220., 230., 240., 250.,
                300., 310., 320., 330., 340., 350.],
            f2=[500., 510., 520., 530., 540., 550.,
                600., 610., 620., 630., 640., 650.]
        ))
        df = self.df[self.df['speaker'] == 'S1'].copy()
        self.s1_centroid = dict(
            f1=(df[df['vowel'] == 'kit']['f1'].values +
                df[df['vowel'] == 'fleece']['f1'].values +
                df[df['vowel'] == 'start']['f1'].values / 2 +
                df[df['vowel'] == 'thought']['f1'].values / 2 +
                df[df['vowel'] == 'trap']['f1'].values) / 4,
            f2=(df[df['vowel'] == 'fleece']['f2'].values +
                df[df['vowel'] == 'goose']['f2'].values +
                df[df['vowel'] == 'start']['f2'].values / 2 +
                df[df['vowel'] == 'thought']['f2'].values / 2 +
                df[df['vowel'] == 'trap']['f2'].values) / 4)

        self.formants = ['f1', 'f2']
        self.kwargs = dict(formants=self.formants)

    def test_fx_spec(self):
        """
        Specify formants using individual keys.
        """
        df = self.df.copy()
        normalizer = self.normalizer()
        normalizer.normalize(
            df, f1='f1', f2='f2', **self.kwargs)
        self.assertListEqual(
            normalizer.params['formants'],
            ['f1', 'f2'])

    def test_fx_list_spec(self):
        """
        Specify formants using individual keys as list.
        """
        df = self.df.copy()
        normalizer = self.normalizer()
        normalizer.normalize(
            df, f1=['f1'], f2=['f2'], **self.kwargs)
        self.assertListEqual(
            normalizer.params['formants'],
            ['f1', 'f2'])

    def test_get_centroid(self):
        """Test get_centroid method."""
        df = self.df.copy()
        df = df[df['speaker'] == 'S1']

        actual = self.normalizer.get_centroid(
            df,
            dict(
                fleece='fleece',
                goose='goose',
                kit='kit',
                start='start',
                thought='thought',
                trap='trap'),
            vowel='vowel',
            f1='f1', f2='f2')
        expected = self.s1_centroid
        self.assertEqual(actual['f1'], expected['f1'])
        self.assertEqual(actual['f2'], expected['f2'])


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
            df, dict(letter='e'), vowel='vowel', formants=['f1', 'f2'])

        expected = Series(
            dict(
                f1=(100. + 200.) / 2,
                f2=(400. + 500.) / 2),
            dtype=actual.dtype)

        assert_series_equal(actual, expected)
