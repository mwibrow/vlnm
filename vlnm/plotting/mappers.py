"""
    Property mappers module
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from collections import OrderedDict
from typing import Any, Callable, Dict, Iterable, List, Union

from matplotlib.cm import get_cmap
import matplotlib.colors
import numpy as np


class Mapper:
    """Class for mapping data values onto plot property values."""

    def __init__(
            self,
            values: Union[dict, Iterable, Callable],
            cycle: bool = False,
            default: any = None):
        self.values = values
        self.cycle = cycle
        self.default = default
        self.indexer = {}

    def get_value(self, value: any, *args, **kwargs):
        """Return a plot property value for a data value."""
        try:
            return self.values(value, *args, **kwargs)
        except TypeError:
            try:
                return self.values.get(value, self.default)
            except AttributeError:
                return self._get_value_iterable(value, *args, **kwargs)

    def _get_value_iterable(self, value, *args, **kwargs):
        try:
            if self.cycle:
                value = value % len(self.values)
            try:
                return self.values[value]
            except IndexError:
                return self.default
        except TypeError:
            index = self.indexer.get(value, len(self.indexer))
            self.indexer[value] = index
            return self._get_value_iterable(index, *args, **kwargs)

    def __getitem__(self, value):
        return self.get_value(value)


def get_prop_mapper(prop: str, value: any, cycle: bool = True, default: any = None) -> Mapper:
    """Factory method for Mapper class."""
    if 'color' in prop:
        return get_color_mapper(value, cycle=cycle, default=default)
    return Mapper(value, cycle=cycle, default=default)


def get_color_mapper(value: any, cycle: bool = False, default: any = None) -> Mapper:
    """Factory method for color mappings."""
    if isinstance(value, matplotlib.colors.Colormap):
        values = list(value.colors)
    if not isinstance(value, list):
        try:
            values = list(get_cmap(value).colors)
        except ValueError:
            values = [value]
    return Mapper(values, cycle=cycle, default=default)


class PropsMapper:

    def __init__(self, **kwargs):
        self.mappers = {}
        self.update(**kwargs)

    def enable_cycles(self, enable=True, prop=None):
        if prop:
            self.mappers[prop].cycle = enable
        else:
            for prp in self.mappers:
                self.mappers[prp].cycle = enable

    def get_props(self, value, *args, **kwargs):
        props = {}
        for prp in self.mappers:
            props.update(**self.get_prop(prp, value, *args, **kwargs))
        return props

    def get_prop(self, prop, value, *args, **kwargs):
        mapper = self.mappers[prop]
        props = mapper.get_value(value, *args, **kwargs)
        if isinstance(props, dict):
            return props
        return {prop: props}

    def update(self, **kwargs):
        self.mappers.update(**{key: Mapper(value) for key, value in kwargs.items()})


class GroupPropsMapper:

    def __init__(self, groups):
        self.groups = OrderedDict({group: PropsMapper() for group in groups})

    def add_mapper(self, group, **kwargs):
        self.groups[group].update(**kwargs)

    def get_props(self, groups, values, *args, **kwargs):
        return {group: self.groups[group].get_props(value, *args, **kwargs)
                for group, value in zip(groups, values)}
