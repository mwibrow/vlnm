"""
Tests for the vlnm.plotting.legends module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import unittest
import unittest.mock as mock

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


class TestLegendCollection(unittest.TestCase):
    """Tests for the LegendCollection class"""

    def test_init(self):
        """Initialise without error"""
        collection = LegendCollection()
        self.assertDictEqual(collection.groups, {})

    def test_add_entry(self):
        """Add an entry to the collection"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1', 'handle1')
        self.assertEqual(collection.groups['group1'].entries['label1'], 'handle1')

    def test_get_item(self):
        """Retrieve group using []"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1', 'handle1')
        self.assertEqual(collection['group1']['label1'], 'handle1')

    def test_get_entries_all(self):
        """Retrieve all entries from all groups"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1-1', 'handle1-1')
        collection.add_entry('group1', 'label1-2', 'handle1-2')
        collection.add_entry('group2', 'label2-1', 'handle2-1')
        entries = collection.get_entries()
        self.assertDictEqual(entries, {
            'label1-1': 'handle1-1',
            'label1-2': 'handle1-2',
            'label2-1': 'handle2-1'
        })

    def test_get_entries_group(self):
        """Retrieve all entries from a group"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1-1', 'handle1-1')
        collection.add_entry('group1', 'label1-2', 'handle1-2')
        collection.add_entry('group2', 'label2-1', 'handle2-1')
        entries = collection.get_entries('group1')
        self.assertDictEqual(entries, {
            'label1-1': 'handle1-1',
            'label1-2': 'handle1-2',
        })

    def test_get_entries_group_entry(self):
        """Retrieve specific entry from a group"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1-1', 'handle1-1')
        collection.add_entry('group1', 'label1-2', 'handle1-2')
        collection.add_entry('group2', 'label2-1', 'handle2-1')
        entries = collection.get_entries('group1', 'label1-2')
        self.assertDictEqual(entries, {
            'label1-2': 'handle1-2',
        })

    def test_get_entries_group_list(self):
        """Retrieve entries from groups"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1-1', 'handle1-1')
        collection.add_entry('group1', 'label1-2', 'handle1-2')
        collection.add_entry('group2', 'label2-1', 'handle2-1')
        collection.add_entry('group3', 'label3-1', 'handle3-1')
        entries = collection.get_entries(['group1', 'group3'])
        self.assertDictEqual(entries, {
            'label1-1': 'handle1-1',
            'label1-2': 'handle1-2',
            'label3-1': 'handle3-1',
        })

    def test_get_entries_all_remove(self):
        """Remove all entries from all groups"""
        collection = LegendCollection()
        collection.add_entry('group1', 'label1-1', 'handle1-1')
        collection.add_entry('group1', 'label1-2', 'handle1-2')
        collection.add_entry('group2', 'label2-1', 'handle2-1')
        removed = collection.get_entries().copy()
        entries = collection.get_entries(remove=True)
        self.assertDictEqual(entries, removed)


class TestLegend(unittest.TestCase):
    """Tests for the Legend class"""

    def test_init(self):
        """Initialise without error"""
        legend = Legend()
        self.assertDictEqual(legend.collection, {})

    def test_add_entry(self):
        """Add an entry to the legend"""
        legend = Legend()
        legend.add_entry('collection1', 'group1', 'label1', 'handle1')
        self.assertEqual(
            legend.collection['collection1'].groups['group1'].entries['label1'], 'handle1')

    def test_get_item(self):
        """Retrieve entry using []"""
        legend = Legend()
        legend.add_entry('collection1', 'group1', 'label1', 'handle1')
        self.assertEqual(
            legend['collection1']['group1']['label1'], 'handle1')

    def test_bool_false(self):
        """Empty collection is falsey"""
        legend = Legend()
        self.assertFalse(legend)

    def test_bool_true(self):
        """Collection with groups is truthy"""
        legend = Legend()
        legend.add_entry('collection1', 'group1', 'label1', 'handle1')
        self.assertTrue(legend)

    def test_get_entries_all(self):
        """Retrieve all entries from all collections"""
        legend = Legend()
        legend.add_entry('collection1', 'group1-1', 'label1-1-1', 'handle1-1-1')
        legend.add_entry('collection1', 'group1-2', 'label1-2-1', 'handle1-2-1')
        legend.add_entry('collection2', 'group2-1', 'label2-1-1', 'handle2-1-1')
        entries = legend.get_entries()
        self.assertDictEqual(entries, {
            'label1-1-1': 'handle1-1-1',
            'label1-2-1': 'handle1-2-1',
            'label2-1-1': 'handle2-1-1'
        })

    def test_get_entries_list(self):
        """Retrieve all entries from list of collections"""
        legend = Legend()
        legend.add_entry('collection1', 'group1-1', 'label1-1-1', 'handle1-1-1')
        legend.add_entry('collection1', 'group1-2', 'label1-2-1', 'handle1-2-1')
        legend.add_entry('collection2', 'group2-1', 'label2-1-1', 'handle2-1-1')
        entries = legend.get_entries(['collection2'])
        self.assertDictEqual(entries, {
            'label2-1-1': 'handle2-1-1'
        })

    def test_get_entries_name(self):
        """Retrieve all entries from specific collections"""
        legend = Legend()
        legend.add_entry('collection1', 'group1-1', 'label1-1-1', 'handle1-1-1')
        legend.add_entry('collection1', 'group1-2', 'label1-2-1', 'handle1-2-1')
        legend.add_entry('collection2', 'group2-1', 'label2-1-1', 'handle2-1-1')
        entries = legend.get_entries('collection1')
        self.assertDictEqual(entries, {
            'label1-1-1': 'handle1-1-1',
            'label1-2-1': 'handle1-2-1',
        })

    def test_get_entries_dot(self):
        """Retrieve all entries using dot notation"""
        legend = Legend()
        legend.add_entry('collection1', 'group1-1', 'label1-1-1', 'handle1-1-1')
        legend.add_entry('collection1', 'group1-2', 'label1-2-1', 'handle1-2-1')
        legend.add_entry('collection2', 'group2-1', 'label2-1-1', 'handle2-1-1')
        entries = legend.get_entries('collection1.group1-2')
        self.assertDictEqual(entries, {
            'label1-2-1': 'handle1-2-1',
        })

    def test_remove_entries_all(self):
        """Remove all entries from all collections"""
        legend = Legend()
        legend.add_entry('collection1', 'group1-1', 'label1-1-1', 'handle1-1-1')
        legend.add_entry('collection1', 'group1-2', 'label1-2-1', 'handle1-2-1')
        legend.add_entry('collection2', 'group2-1', 'label2-1-1', 'handle2-1-1')
        removed = legend.get_entries().copy()
        entries = legend.get_entries(remove=True)
        self.assertDictEqual(entries, removed)
        self.assertFalse(legend)

    @mock.patch('matplotlib.pyplot.legend')
    def test_make_legend_artist_empty(self, mock_legend):
        """No entries returns none"""
        legend = Legend()
        artist = legend.make_legend_artist()
        self.assertIsNone(artist)

    @mock.patch('matplotlib.pyplot.legend')
    def test_make_legend_artist(self, mock_legend):
        """Return artist if entries in the legend collection"""

        legend = Legend()
        legend.add_entry('collection1', 'group1', 'label1', 'handle1')
        artist = legend.make_legend_artist()
        self.assertIsNotNone(artist)
        mock_legend.assert_called_with(
            handles=('handle1',),
            labels=('label1',)
        )

    @mock.patch('matplotlib.pyplot.legend', new=lambda **kwargs: kwargs)
    def test_make_legend_artist_modify(self):
        """Modify artist in the legend collection"""
        legend = Legend()
        # Exploit fact that dict has update method.
        legend.add_entry('collection1', 'group1', 'label1', {'key': 'value'})
        artist = legend.make_legend_artist(entry=dict(key='alternative'))
        self.assertEqual(artist['handles'][0]['key'], 'alternative')
