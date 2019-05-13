"""
Test for the utils module.
"""

import unittest

from vlnm.utils import (
    merge_columns,
    flatten,
    nameify,
    quote_item,
    str_or_list,
    get_formants_spec)

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

    def test_no_args(self):
        """
        No args returns empty string.
        """
        self.assertEqual('', nameify([]))

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

    def test_single_argument(self):
        """
        Single argument quoted with no junctions
        """
        items = [1]
        expected = "'1'"
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


class TestQuoteItem(unittest.TestCase):
    """Test the quote_item function"""

    def test_quote_item(self):
        """Sunny day test."""
        self.assertEqual('"test"', quote_item('test', '"'))


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


class TestGetFormantsSpec(unittest.TestCase):
    """
    Tests for the get_formant_spec function.
    """

    def test_default(self):
        """
        Nothing specified returns dictionary with default keys.
        """
        columns = ['f0', 'f1', 'f2', 'f3']
        expected = dict(
            f0=['f0'], f1=['f1'], f2=['f2'], f3=['f3'], formants=columns)
        actual = get_formants_spec()
        self.assertDictEqual(actual, expected)

    def test_fx_string(self):
        """
        Coerce fx as string to list.
        """
        columns = ['f0', 'f1']
        expected = dict(
            f0=['f0'], f1=['f1'], f2=[None], f3=[None], formants=columns)
        actual = get_formants_spec(f0='f0', f1='f1')
        self.assertDictEqual(actual, expected)

    def test_formants_list(self):
        """
        Formants keyword should return only keyword.
        """
        formants = ['f0', 'f1']
        expected = dict(formants=formants)
        actual = get_formants_spec(formants=formants)
        self.assertDictEqual(actual, expected)

    def test_formants_special(self):
        """
        Formants ['f0', 'f1', 'f2', 'f3'] returns full spec.
        """
        formants = ['f0', 'f1', 'f2', 'f3']
        expected = dict(
            f0=['f0'], f1=['f1'], f2=['f2'], f3=['f3'], formants=formants)
        actual = get_formants_spec(formants=formants)
        self.assertDictEqual(actual, expected)
