"""
Test for the utils module.
"""

import unittest

import pandas as pd

from vlnm.utils import (
    check_data_frame_columns,
    check_one_from_kwargs,
    check_required_kwargs,
    flatten,
    str_or_list)


class TestFlatten(unittest.TestCase):
    """
    Tests for the flatten function
    """

    def test_empty(self):
        """
        Empty list returns empty list.
        """
        actual = flatten([])
        self.assertEqual(len(actual), 0)

    def test_list_of_empty_lists(self):
        """
        List of empty lists returns empty list.
        """
        actual = flatten([[], [[]], []])
        self.assertEqual(len(actual), 0)

    def test_nested_lists(self):
        """
        Nested lists.
        """
        expected = ['a', 'b', 'c', 'd']
        actual = flatten(['a', ['b', 'c'], [['d']]])
        self.assertListEqual(actual, expected)


class TestStrOrList(unittest.TestCase):
    """
    Tests for the str or list function
    """

    def test_none(self):
        """
        None returns list of stringified None
        """
        actual = str_or_list(None)
        self.assertListEqual(actual, [None])

    def test_str(self):
        """
        String returns list of str
        """
        value = 'value'
        actual = str_or_list(value)
        self.assertListEqual(actual, [value])

    def test_list(self):
        """
        List returns list
        """
        value = ['value']
        actual = str_or_list(value)
        self.assertListEqual(actual, value)


class TestDataFrameColumns(unittest.TestCase):
    """
    Test the check_data_frame_columns function.
    """

    def test_empty(self):
        """No columns."""
        self.assertIsNone(check_data_frame_columns(
            pd.DataFrame(),
            []))

    def test_missing(self):
        """Missing column."""
        expected = 'column'
        actual = check_data_frame_columns(
            pd.DataFrame(),
            [expected])
        self.assertEqual(actual, expected)

    def test_present(self):
        """Column in data frame."""
        actual = check_data_frame_columns(
            pd.DataFrame(dict(column=[1, 2, 3])),
            ['column'])
        self.assertIsNone(actual)


class TestCheckRequiredKwargs(unittest.TestCase):
    """
    Tests for the check_required_kwargs function.
    """

    def test_empty(self):
        """No required keyword arguments."""
        self.assertIsNone(check_required_kwargs({}, []))

    def test_missing(self):
        """Missing keyword arugment."""
        expected = 'keyword'
        actual = check_required_kwargs({}, ['keyword'])
        self.assertEqual(actual, expected)

    def test_present(self):
        """Required keyword argument(s) present."""
        actual = check_required_kwargs(
            dict(keyword1=1, keyword2=2),
            ['keyword1', 'keyword2'])
        self.assertIsNone(actual)


class TestCheckOneFromKwargs(unittest.TestCase):
    """
    Test the check_one_from_kwargs function.
    """

    def test_empty(self):
        """No as least one-from keyword arguments."""
        self.assertIsNone(check_one_from_kwargs({}, []))

    def test_missing(self):
        """Missing all one-from keyword arguments."""
        one_from = [['keyword1', 'keyword2']]
        expected = one_from
        actual = check_one_from_kwargs({}, one_from)
        self.assertEqual(actual, expected)

    def test_present(self):
        """At least one-from keyword argument present."""
        one_from = [['keyword1', 'keyword2']]
        actual = check_one_from_kwargs(
            dict(keyword2=2),
            one_from)
        self.assertIsNone(actual)
