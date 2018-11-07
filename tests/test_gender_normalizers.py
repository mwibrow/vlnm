"""
Tests for the normalizers which require speakers to identify as female or male.
"""

import unittest

from vlnm.conversion import hz_to_bark
from vlnm.normalizers.gender import (
    BladenNormalizer,
    NordstromNormalizer)
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


class TestBladenNormalizer(unittest.TestCase):
    """
    Test the BladenNormalizer.
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
        self.kwargs = {}
        self.formants = ['f0', 'f1', 'f2', 'f3']

    def test_output(self):
        """Test output."""
        normalizer = BladenNormalizer()

        df = self.df.copy()
        expected = hz_to_bark(df[self.formants])
        expected[df['gender'] == 'F'] -= 1.
        actual = normalizer.normalize(
            df,
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
            gender='sex',
            female='F',
            male='M',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))


class TestNordstromNormalizer(unittest.TestCase):
    """
    Tests for the NordstromNormalizer class.
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
        self.kwargs = {}
        self.formants = ['f0', 'f1', 'f2', 'f3']

    def test_prenormalize(self):
        """Calculate mu ratios."""
        df = self.df
        mu_male = df[(df['gender'] == 'M') & (df['f1'] > 600)]['f3'].mean()
        mu_female = df[(df['gender'] == 'F') & (df['f1'] > 600)]['f3'].mean()

        constants = {}
        NordstromNormalizer.get_f3_means(
            df,
            constants=constants,
            gender='gender',
            male='M',
            female='F')
        self.assertEqual(constants['mu_female'], mu_female)
        self.assertEqual(constants['mu_male'], mu_male)

    def test_output(self):
        """Test output of Nordstrom normalizer."""
        df = self.df
        actual = NordstromNormalizer().normalize(
            df, gender='gender', female='F', male='M')
        self.assertTrue(actual is not None)
