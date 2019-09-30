"""
Module for handling legends.
"""

from collections import OrderedDict
from typing import Union

from matplotlib.artist import Artist
import matplotlib.pyplot as plt

TRANSLATOR = dict(
    position={
        'bottom': dict(
            loc='upper center', bbox_to_anchor=(0.5, 0),
        ),
        'bottom right': dict(
            loc='lower left', bbox_to_anchor=(1, 0),
        ),
        'top': dict(
            loc='lower center', bbox_to_anchor=(0.5, 1),
        ),
        'top right': dict(
            loc='upper left', bbox_to_anchor=(1, 1),
        ),
        'right': dict(
            loc='center left', bbox_to_anchor=(1, 0.5)
        ),
        'left': dict(
            loc='center right', bbox_to_anchor=(0, 0.5)
        )
    }
)


def translate_legend_options(**options):
    """Translate between custom legend keyword arguments and matplotlib keywords."""
    legend_options = {}
    for key, value in options.items():
        if key in TRANSLATOR:
            if value in TRANSLATOR[key]:
                legend_options.update(**TRANSLATOR[key][value])
            else:
                raise ValueError(
                    "Invalid value '{}' for legend option '{}'. Expected one of {}.".format(
                        value, key, ', '.join("'{}'".format(prop) for prop in TRANSLATOR[key])
                    ))
        else:
            legend_options[key] = value
    return legend_options


class LegendGroup:

    def __init__(self):
        self.entries = OrderedDict()

    def add_entry(self, label, handle):
        self.entries[label] = handle

    def values(self):
        return self.entries.values()

    def keys(self):
        return self.entries.keys()

    def get_entries(self, labels=None):
        if not labels:
            entries = self.entries.keys()
        elif isinstance(labels, list):
            entries = labels
        else:
            entries = [labels]

        return [(name, self.entries[name]) for name in entries]

    def __getitem__(self, label):
        return self.entries[label]


class LegendCollection:

    def __init__(self):
        self.groups = OrderedDict()

    def add_entry(self, group, label, handle):
        if not group in self.groups:
            self.groups[group] = LegendGroup()
        self.groups[group].add_entry(label, handle)

    def get_entries(self, group=None, labels=None):
        if not group:
            groups = list(self.groups.keys())
        elif isinstance(group, list):
            groups = group
        else:
            groups = [group]

        entries = []
        for name in groups:
            entries.extend(self.groups[name].get_entries(labels))
        return entries

    def __getitem__(self, group):
        return self.groups[group]

    def __iter__(self):
        for group in self.groups:
            yield group


class Legend:

    def __init__(self):
        self.collection = OrderedDict()

    def add_entry(self, collection_id, group, label, handle):
        if not collection_id in self.collection:
            self.collection[collection_id] = LegendCollection()
        self.collection[collection_id].add_entry(group, label, handle)

    def get_entries(self, collection=None, group=None, labels=None):

        if not collection:
            collections = list(self.collection.keys())
        elif isinstance(collection, list):
            collections = collection
        else:
            if '.' in collection:
                collection, group, entries = *collection.split('.'), None
            collections = [collection]

        _entries = []
        for name in collections:
            _entries.extend(self.collection[name].get_entries(group, labels))

        return _entries

    def make_legend_artist(
            self,
            collection: Union[str, list] = None,
            group: Union[str, list] = None,
            labels: Union[str, list] = None,
            entry: dict = None,
            **options) -> Artist:
        legend_entries = self.get_entries(collection, group, labels)
        if legend_entries:
            labels, handles = zip(*legend_entries)
            if entry:
                for handle in handles:
                    handle.update(entry)

            options = translate_legend_options(**options)
            options['handles'] = options.get('handles', handles)
            options['labels'] = options.get('labels', labels)
            artist = plt.legend(**options)
            return artist
        return None

    def __getitem__(self, collection_id):
        return self.collection[collection_id]

    def __bool__(self):
        return bool(self.collection)
