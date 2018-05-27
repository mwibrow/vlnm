"""
Test for the utils module.
"""

import unittest

from vlnm.utils import (
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
