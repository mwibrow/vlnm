"""
Tests for the vlnm.plotting.legends module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest

from vlnm.plotting.legends import (
    Legend,
    LegendCollection,
    LegendGroup,
    translate_legend_options,
    TRANSLATOR,
)


class TestTranslateLegendOptions(unittest.TestCase):
    """Tests for the translate_legend_options function"""

    def test_no_options(self):
        """No options returns empty dict"""
        options = translate_legend_options()
        self.assertDictEqual(options, {})

    def test_no_translation(self):
        """Non-translatable options returned unchanged"""
        expected = dict(a=1, b=2)
        actual = translate_legend_options(**expected)
        self.assertDictEqual(actual, expected)

    def test_translate_position(self):
        """Position option translated"""
        expected = dict(a=1, b=2, **TRANSLATOR['position']['bottom'])
        actual = translate_legend_options(a=1, b=2, position='bottom')
        self.assertDictEqual(actual, expected)

    def test_translate_invalid_position(self):
        """Invalid position option raises error"""
        with self.assertRaises(ValueError):
            translate_legend_options(position='INVALID')


class TestLegendGroup(unittest.TestCase):
    """Tests for the LegendGroup class"""

    def test_init(self):
        """Initialise without error"""
        group = LegendGroup()
        self.assertDictEqual(group.entries, {})

    def test_add_entry(self):
        """Add entry to the group"""
        group = LegendGroup()
        group.add_entry('label', 'handle')
        self.assertDictEqual(group.entries, {'label': 'handle'})

    def test_get_item(self):
        """Retrieve entry using []"""
        group = LegendGroup()
        group.add_entry('label', 'handle')
        self.assertEqual(group['label'], 'handle')

    def test_get_entries_all(self):
        """No label returns all entries"""
        group = LegendGroup()
        group.add_entry('label1', 'handle1')
        group.add_entry('label2', 'handle2')
        entries = group.get_entries()
        self.assertDictEqual(entries, group.entries)

    def test_get_entries_specific(self):
        """Label string returns specific entries"""
        group = LegendGroup()
        group.add_entry('label1', 'handle1')
        group.add_entry('label2', 'handle2')
        entries = group.get_entries('label1')
        self.assertDictEqual(entries, {'label1': 'handle1'})

    def test_get_entries_list(self):
        """Label list returns specific entries in order"""
        group = LegendGroup()
        group.add_entry('label1', 'handle1')
        group.add_entry('label2', 'handle2')
        group.add_entry('label3', 'handle3')

        labels = ['label3', 'label1']
        entries = group.get_entries(['label3', 'label1'])
        self.assertListEqual(list(entries.keys()), labels)
        self.assertDictEqual(entries, {'label1': 'handle1', 'label3': 'handle3'})

    def test_get_entries_remove_all(self):
        """Remove all entries"""
        group = LegendGroup()
        group.add_entry('label1', 'handle1')
        group.add_entry('label2', 'handle2')
        removed = group.entries.copy()
        entries = group.get_entries(remove=True)
        self.assertDictEqual(entries, removed)
        self.assertEqual(len(group.entries), 0)

    def test_get_entries_remove_specific(self):
        """Remove specific entry"""
        group = LegendGroup()
        group.add_entry('label1', 'handle1')
        group.add_entry('label2', 'handle2')
        removed = {'label2': 'handle2'}
        entries = group.get_entries('label2', remove=True)
        self.assertDictEqual(entries, removed)
        self.assertEqual(len(group.entries), 1)
