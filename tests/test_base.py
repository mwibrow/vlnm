"""
Tests for normalizer base classes
"""

import unittest

from vlnm.normalizers.base import (
    FormantIntrinsicNormalizer,
    VowelNormalizer)

from tests.test_normalizers import (
    get_test_dataframe
)

class TestVowelNormalizer(unittest.TestCase):
    """
    Tests for the VowelNormalizer class
    """

    def setUp(self):
        self.df = get_test_dataframe()

    def test_default(self):
        """Sunny day test."""
        VowelNormalizer().normalize(self.df)

    def test_rename(self):
        """Sunny day rename test."""
        VowelNormalizer().normalize(self.df, rename='{}_N')


class TestFormantIntrinsicNormalizer(unittest.TestCase):
    """
    Tests for the FormantIntrinsicNormalizer class
    """

    def setUp(self):
        self.df = get_test_dataframe()

    def test_default(self):
        """Sunny day test."""
        FormantIntrinsicNormalizer().normalize(self.df)

    def test_reanme(self):
        """Sunny day rename test."""
        FormantIntrinsicNormalizer().normalize(self.df, rename='{}_N')
