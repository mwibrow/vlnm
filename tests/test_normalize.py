"""
Tests for the normalize module.
"""

import unittest

import pandas as pd

from vlnm.normalize import (
    check_kwargs,
    columns_in_dataframe)


class TestCheckKwargs(unittest.TestCase):
    """
    Tests for the check_kwargs function.
    """

    def test_empty(self):
        """All empty arguments"""
        required, one_of = check_kwargs({})
        self.assertIsNone(required)
        self.assertIsNone(one_of)

    def test_required_missing(self):
        """Missing required argument"""
        required, one_of = check_kwargs({}, required=['missing'])
        self.assertIsNotNone(required)
        self.assertIsNone(one_of)

    def test_required(self):
        """Required argument passes"""
        required, one_of = check_kwargs(
            dict(present='here'), required=['present'])
        self.assertIsNone(required)
        self.assertIsNone(one_of)

    def test_one_of_missing(self):
        """Missing one-of argument"""
        required, one_of = check_kwargs({}, one_of=[['missing']])
        self.assertIsNone(required)
        self.assertIsNotNone(one_of)

    def test_one_of(self):
        """One-of argument passes"""
        required, one_of = check_kwargs(
            dict(present='here'),
            one_of=[['present', 'and', 'correct']])
        self.assertIsNone(required)
        self.assertIsNone(one_of)


class TestColumnsInDataFrame(unittest.TestCase):
    """
    Test the columns_in_dataframe function
    """

    def test_empty(self):
        """No dataframe and no columns"""
        self.assertTrue(columns_in_dataframe(pd.DataFrame()))

    def test_in(self):
        """Columns in dataframe"""
        self.assertTrue(
            columns_in_dataframe(
                pd.DataFrame(dict(a=[1, 2], b=[3, 4])),
                ['a'], ['b']))

    def test_nested(self):
        """Nested columns in dataframe"""
        self.assertTrue(
            columns_in_dataframe(
                pd.DataFrame(dict(a=[1, 2], b=[3, 4], c=[5, 6])),
                ['a', ['b']], ['c']))
