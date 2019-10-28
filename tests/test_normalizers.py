"""
Tests for the normalizer package.
"""

import unittest

from vlnm import (
    get_normalizer,
    list_normalizers)
from vlnm.registration import register_normalizer


class TestGetNormalizer(unittest.TestCase):
    """
    Tests for the get_normalizer function.
    """

    def test_empty_method(self):
        """
        Empty string raises ValueError.
        """
        with self.assertRaises(ValueError):
            get_normalizer('')

    def test_unknown_method(self):
        """
        Invalid method raises NameError.
        """
        with self.assertRaises(NameError):
            get_normalizer('test_normalizer')

    def test_ambiguous_method(self):
        """
        Ambiguous method fraises NameError.
        """
        index = dict(
            test_normalizer1=True,
            test_normalizer2=False)
        with self.assertRaises(NameError):
            get_normalizer('test_normalizer', index=index)

    def test_retrieve_normalizer(self):
        """
        Return value in index.
        """
        index = dict(
            test_normalizer1=True,
            test_normalizer2=False)
        expected = True
        actual = get_normalizer('test_normalizer1', index=index)
        self.assertEqual(actual, expected)


class TestListNormalizers(unittest.TestCase):
    """
    Tests for the list_normalizers function.
    """

    def test_list_no_normalizers(self):
        """
        List normalizers returns empty list.
        """
        expected = []
        actual = list_normalizers(index={})
        self.assertListEqual(actual, expected)


class TestRegisterNormalizers(unittest.TestCase):
    """
    Test the register_normalizer function.
    """

    def test_register_normalizer(self):
        """
        Register a normalizer.
        """
        # Doesn't actually need to be a class.
        actual = {}
        register_normalizer(True, 'test', index=actual)
        self.assertDictEqual(actual, {'test': True})


class WholeBunchOfChanges:
    pass
