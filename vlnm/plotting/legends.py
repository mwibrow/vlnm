"""
Module for handling legends.
"""

from collections import OrderedDict

TRANSLATOR = dict(
    position={
        'bottom': dict(
            loc='upper center', bbox_to_anchor=(0.5, 0),
        ),
        'top': dict(
            loc='lower center', bbox_to_anchor=(0.5, 1),
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
    for key, value in options:
        if key in TRANSLATOR:
            if value in TRANSLATOR[key]:
                legend_options.update(**TRANSLATOR[key][value])
            else:
                raise ValueError(
                    "Invalid value '{}' for legend option '{}'. Expected one of {}.".format(
                        value, key, ', '.join("'{}'".format(prop) for prop in TRANSLATOR[key])
                    ))
    return legend_options


class LegendGroup:

    def __init__(self, parent=None):
        self.entries = OrderedDict()
        self.parent = parent
        self.options = {**parent.options} if parent else {}

    def add_entry(self, label, handle):
        self.entries[label] = handle

    def update_options(self, **options):
        self.options.update(**options)

    def get_options(self, parent=True):
        if parent and self.parent:
            return {**self.parent.options, **self.options}
        return self.options

    def __getitem__(self, label):
        return self.entries[label]


class LegendCollection:

    def __init__(self, parent=None):
        self.groups = OrderedDict()
        self.parent = parent
        self.options = {**parent.options} if parent else {}

    def add_entry(self, group, label, handle):
        if not group in self.groups:
            self.groups[group] = LegendGroup(self)
        self.groups[group].add_entry(label, handle)

    def update_options(self, **options):
        self.options.update(**options)

    def get_options(self, parent=True):
        if parent and self.parent:
            return {**self.parent.options, **self.options}
        return self.options

    def __getitem__(self, group):
        return self.groups[group]


class Legend:

    def __init__(self, options=None):
        self.collection = OrderedDict()
        self.options = options or {}

    def add_entry(self, collection_id, group, label, handle):
        if not collection_id in self.collection:
            self.collection[collection_id] = LegendCollection()
        self.collection[collection_id].add_entry(group, label, handle)

    def update_options(self, collection_id=None, **options):
        if collection_id:
            if not collection_id in self.collection:
                self.collection[collection_id] = LegendCollection()
                self.collection[collection_id].update(**options)
        else:
            self.options.update(**options)

    def get_options(self, collection_id=None, group=None):
        if collection_id and group:
            return translate_legend_options(
                **self.collection[collection_id].groups[group].get_options())
        if collection_id:
            return translate_legend_options(
                **self.collection[collection_id].get_options())
        return translate_legend_options(**self.options)

    def __getitem__(self, collection_id):
        return self.collection[collection_id]

    def __bool__(self):
        return bool(self.collection)
