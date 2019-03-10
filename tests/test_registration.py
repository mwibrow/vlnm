"""
Tests for registering normalizer classes
"""

import unittest

from vlnm.registration import register_normalizer, NORMALIZERS


class _TestNormalizer:
    def public_method(self):
        """A public method for the linter."""


class TestRegisterNormalizer(unittest.TestCase):
    """
    Test the register_normalizer function.
    """

    def test_default_register(self):
        """Add an entry to the default index"""
        register_normalizer(_TestNormalizer, 'test')

        def is_subdict(small, big):
            return dict(big, **small) == big

        self.assertDictEqual(
            NORMALIZERS,
            dict(NORMALIZERS, **dict(test=_TestNormalizer)))

    def test_custom_index(self):
        """Add an entry to a custom index"""
        actual = {}
        register_normalizer(_TestNormalizer, 'test', index=actual)
        self.assertDictEqual(
            actual,
            dict(test=_TestNormalizer))
