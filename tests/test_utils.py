"""
Test for the utils module.
"""

import unittest

import pandas as pd

from vlnm.utils import (
    merge_columns,
    flatten,
    nameify,
    str_or_list)

class TestMergeColumns(unittest.TestCase):
    """
    tests for the merge_columns
    """

    def test_merge_columns(self):
        """
        test something
        """
        required = dict(
            required='speaker',
            formants=['f0', 'f1', 'f2', 'f3']
        )
        kwargs = {}
        kwargs = merge_columns(required, {})
        for kwarg in ['speaker', 'f0', 'f1', 'f2', 'f3']:
            self.assertIn(kwarg, kwargs)



class TestNameify(unittest.TestCase):
    """
    Tests for the nameify function
    """

    def test_default(self):
        """
        Default args.
        """
        items = [1, 2, 3, 4]
        expected = '1, 2, 3, 4'
        actual = nameify(items)
        self.assertEqual(actual, expected)

    def test_sep(self):
        """
        Different separator
        """
        items = [1, 2, 3, 4]
        expected = '1| 2| 3| 4'
        actual = nameify(items, sep='|')
        self.assertEqual(actual, expected)

    def test_junction(self):
        """
        Add (con)junction
        """
        items = [1, 2, 3, 4]
        expected = '1, 2, 3 and 4'
        actual = nameify(items, junction='and')
        self.assertEqual(actual, expected)

    def test_oxford(self):
        """
        Use oxford comma
        """
        items = [1, 2, 3, 4]
        expected = '1, 2, 3, and 4'
        actual = nameify(items, junction='and', oxford=True)
        self.assertEqual(actual, expected)

    def test_quote(self):
        """
        Use quotes
        """
        items = [1, 2, 3, 4]
        expected = "'1', '2', '3', '4'"
        actual = nameify(items, quote="'")
        self.assertEqual(actual, expected)

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
