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

    def get_entries(self, entries=None):
        if not entries:
            _entries = self.entries.keys()
        elif isinstance(entries, list):
            _entries = entries
        else:
            _entries = [entries]

        return [(name, self.entries[name]) for name in _entries]

    def __getitem__(self, label):
        return self.entries[label]


class LegendCollection:

    def __init__(self):
        self.groups = OrderedDict()

    def add_entry(self, group, label, handle):
        if not group in self.groups:
            self.groups[group] = LegendGroup()
        self.groups[group].add_entry(label, handle)

    def get_entries(self, group=None, entries=None):
        if not group:
            groups = list(self.groups.keys())
        elif isinstance(group, list):
            groups = group
        else:
            groups = [group]

        _entries = []
        for name in self.groups:
            _entries.extend(self.groups[name].get_entries(entries))
        return _entries

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

    def get_entries(self, collection=None, group=None, entries=None):

        if not collection:
            collections = list(self.collection.keys())
        elif isinstance(collection, list):
            collections = collection
        else:
            collections = [collection]

        _entries = []
        for name in collections:
            _entries.extend(self.collection[name].get_entries(group, entries))

        return _entries

    def make_legend_artist(
            self,
            collection: Union[str, list] = None,
            group: Union[str, list] = None,
            entries: Union[str, list] = None,
            **options) -> Artist:
        _entries = self.get_entries(collection, group, entries)
        if _entries:
            _labels, _handles = zip(*_entries)
            _options = translate_legend_options(**options)
            artist = plt.legend(
                handles=_handles,
                labels=_labels,
                **_options)
            return artist
        return None

    def __getitem__(self, collection_id):
        return self.collection[collection_id]

    def __bool__(self):
        return bool(self.collection)
