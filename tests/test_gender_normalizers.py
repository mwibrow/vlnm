"""
Tests for the normalizers which require speakers to identify as female or male.
"""

import unittest

from vlnm.conversion import (
    hz_to_bark)
from vlnm.normalizers.normalizers import (
    BladenNormalizer,
    NordstromNormalizer)
from vlnm.normalizers.validation import (
    ChoiceKeywordMissingError,
    RequiredColumnMissingError,
    RequiredColumnAliasMissingError)
from tests.helpers import (
    generate_data_frame,
    BaseTestCases)

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


class TestBladenNormalizer(BaseTestCases.BaseTestNormalizer):
    """
    Test the BladenNormalizer.
    """
    normalizer = BladenNormalizer
    required_kwargs = dict(
        female='F')

    def test_no_male_or_female(self):
        """No female or male column raises Error."""
        with self.assertRaises(ChoiceKeywordMissingError):
            BladenNormalizer().normalize(
                self.df, gender='gender', **self.kwargs)

    def test_minimal_kwargs(self):
        """Minimally correct kwargs."""
        BladenNormalizer().normalize(
            self.df,
            gender='gender', male='M', **self.kwargs)

    def test_with_female(self):
        """Test specifying female label."""
        normalizer = BladenNormalizer()

        expected = hz_to_bark(self.df.copy()[self.formants])
        expected[self.df['gender'] == 'F'] -= 1.
        actual = normalizer.normalize(
            self.df,
            gender='gender',
            female='F',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))

    def test_with_male(self):
        """Test specifying male label."""
        normalizer = BladenNormalizer()
        expected = hz_to_bark(self.df.copy()[self.formants])
        expected[self.df['gender'] == 'F'] -= 1.
        actual = normalizer.normalize(
            self.df,
            gender='gender',
            male='M',
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
            aliases=dict(gender='sex'),
            female='F',
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))

    def test_gender_alias_keyword(self):
        """Test keyword aliased gender column."""
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
            **self.kwargs)[self.formants]
        self.assertTrue(actual.equals(expected))


class TestNordstromNormalizer(unittest.TestCase):
    """
    Tests for the NordstromNormalizer class.
    """

    normalizer = NordstromNormalizer
    required_kwargs = dict(
        female='F')

    def setUp(self):
        self.df = DATA_FRAME.copy()
        self.formants = ['f2', 'f3']
        self.kwargs = dict(
            formants=self.formants)

    def test_no_female_or_male_label(self):
        """No female or male label raise error."""
        with self.assertRaises(ChoiceKeywordMissingError):
            NordstromNormalizer().normalize(self.df)

    def test_mu_ratio(self):
        """Calculate mu ratios."""
        df = self.df
        mu_male = df[(df['gender'] == 'M') & (df['f1'] > 600)]['f3'].mean()
        mu_female = df[(df['gender'] == 'F') & (df['f1'] > 600)]['f3'].mean()

        constants = {}
        NordstromNormalizer.calculate_f3_means(
            df,
            constants=constants,
            gender='gender',
            female='F')
        self.assertEqual(constants['mu_female'], mu_female)
        self.assertEqual(constants['mu_male'], mu_male)

    def test_output(self):
        """Test output of Nordstrom normalizer."""
        df = self.df
        actual = NordstromNormalizer().normalize(
            df, gender='gender', female='F')
        self.assertTrue(actual is not None)
