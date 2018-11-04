"""
Tests for the normalize module.
"""

# pylint: disable=protected-access

import unittest

from vlnm.conversion import hz_to_bark
from vlnm.normalizers.vowel import BarkDifferenceNormalizer
from tests.helpers import generate_data_frame


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

class TestBarkDifferenceNormalizer(unittest.TestCase):
    """
    Test the BarkDifferenceNormalizer class
    """

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict()

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
