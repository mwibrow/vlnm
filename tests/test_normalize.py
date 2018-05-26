"""
Tests for the normalize module.
"""

import unittest


from vlnm.normalize import check_kwargs


class TestCheckKwargs(unittest.TestCase):
    """
    Tests for the check_kwargs function.
    """

    def test_empty(self):
        """All empty arguments"""
        self.assertIsNone(
            check_kwargs('', {}))

    def test_required_missing(self):
        """Missing required argument raises value error"""
        with self.assertRaises(ValueError):
            check_kwargs('', {}, required=['missing'])

    def test_required(self):
        """Required argument passes"""
        self.assertIsNone(
            check_kwargs('', dict(present='here'), required=['present']))

    def test_one_of_missing(self):
        """Missing one-of argument raises value error"""
        with self.assertRaises(ValueError):
            check_kwargs('', {}, one_of=[['missing']])

    def test_one_of(self):
        """One-of argument passes"""
        self.assertIsNone(
            check_kwargs(
                '',
                dict(present='here'),
                one_of=[['present', 'and', 'correct']]))
