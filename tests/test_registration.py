"""
Tests for registering normalizer classes
"""

import unittest

import vlnm.normalizers
from vlnm.normalizers import (
    Register, register_normalizer
)

class _TestNormalizer:
    def public_method(self):
        """A public method for the linter."""

class TestRegisterNormalizer(unittest.TestCase):
    """
    Test the register_normalizer function.
    """

    def test_default_register(self):
        """Add an entry to the default register"""
        vlnm.normalizers.NORMALIZERS = {}
        register_normalizer(_TestNormalizer, 'test')
        self.assertDictEqual(
            vlnm.normalizers.NORMALIZERS,
            dict(test=_TestNormalizer))

    def test_custom_register(self):
        """Add an entry to a custom register"""
        actual = {}
        register_normalizer(_TestNormalizer, 'test', register=actual)
        self.assertDictEqual(
            actual,
            dict(test=_TestNormalizer))


class TestRegisterDecorator(unittest.TestCase):
    """
    Test the Register decorator.
    """

    def test_default_register(self):
        """Add an entry to the default register."""

        vlnm.normalizers.NORMALIZERS = {}

        @Register('test1')
        class _TestRegister1:
            def public_method(self):
                """A public method for the linter."""

        self.assertDictEqual(
            vlnm.normalizers.NORMALIZERS,
            dict(test1=_TestRegister1))
