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
    get_formant_columns,
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


class TestGetFormantColumns(unittest.TestCase):
    """
    Test the get_formant_columns function.
    """

    def test_no_formant(self):
        """
        No formant returns empty list.
        """
        columns = ['f0', 'f1', 'f2', 'f3']
        expected = []
        actual = get_formant_columns([], columns)
        self.assertListEqual(actual, expected)

    def test_re(self):
        """
        Regular expression matches exactly.
        """
        columns = ['f0', 'f0@50', 'f1']
        expected = ['f0', 'f0@50']
        actual = get_formant_columns(r'f0.*', columns)
        self.assertListEqual(actual, expected)

    def test_list(self):
        """
        List of columns
        """
        columns = ['f0', 'f0@50', 'f1']
        expected = ['f0', 'f0@50']
        actual = get_formant_columns(['f0', 'f0@50'], columns)
        self.assertListEqual(actual, expected)


class TestGetFormantsSpec(unittest.TestCase):
    """
    Tests for the get_formant_spec function.
    """

    def test_default(self):
        """
        Nothing specified returns dictionary with default keys.
        """
        columns = ['f0', 'f1']
        expected = dict(f0=['f0'], f1=['f1'], formants=columns)
        actual = get_formants_spec(columns)
        self.assertDictEqual(actual, expected)

    def test_fx_string(self):
        """
        Fx specified as string returns dictionary with specified keys.
        """
        columns = ['f0', 'f1']
        expected = dict(f0=['f0'], f1=['f1'], formants=columns)
        actual = get_formants_spec(columns, f0='f0', f1='f1')
        self.assertDictEqual(actual, expected)

    def test_fx_list(self):
        """
        Fx specified as list returns dictionary with specified keys.
        """
        columns = ['f0', 'f1']
        expected = dict(f0=['f0'], f1=['f1'], formants=columns)
        actual = get_formants_spec(columns, f0=['f0'], f1=['f1'])
        self.assertDictEqual(actual, expected)

    def test_fx_regex(self):
        """
        Fx specified as regex returns dictionary with specified keys.
        """
        columns = ['f0', 'f0@50', 'f1', 'f1@50']
        expected = dict(
            f0=['f0', 'f0@50'], f1=['f1', 'f1@50'], formants=columns)
        actual = get_formants_spec(columns, f0='f0.*', f1='f1.*')
        self.assertDictEqual(actual, expected)

    def test_formants_dict(self):
        """
        formants specified as dict returns dictionary with specified keys.
        """
        columns = ['f0', 'f0@50', 'f1', 'f1@50']
        expected = dict(f0=['f0'], f1=['f1'], formants=['f0', 'f1'])
        actual = get_formants_spec(columns, formats=dict(
            f0='f0', f1='f1'))
        self.assertDictEqual(actual, expected)

    def test_formants_regex(self):
        """
        formants specified as regex returns dictionary with formant key.
        """
        columns = ['f0', 'f0@50', 'f1', 'f1@50']
        expected = dict(formants=['f0', 'f1', 'f0@50', 'f1@50'])
        actual = get_formants_spec(columns, formants=r'f.*')
        self.assertIn('formants', actual)
        self.assertEqual(len(list(actual.keys())), 1)
        self.assertListEqual(
            sorted(actual['formants']),
            sorted(expected['formants']))

    def test_formants_list(self):
        """
        formants specified as list returns dictionary with formant key.
        """
        columns = ['f0', 'f0@50', 'f1', 'f1@50']
        expected = dict(formants=['f0', 'f1'])
        actual = get_formants_spec(columns, formants=['f0', 'f1'])
        self.assertIn('formants', actual)
        self.assertEqual(len(list(actual.keys())), 1)
        self.assertListEqual(
            sorted(actual['formants']),
            sorted(expected['formants']))
