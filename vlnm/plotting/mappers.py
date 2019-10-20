"""
    Property mappers module
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from collections import OrderedDict
from typing import Any, Callable, Dict, Iterable, List, Union

from matplotlib.cm import get_cmap
import matplotlib.colors
from pandas.api.types import is_categorical_dtype
import numpy as np


class PropMapper:
    """Class for managing the mapping of data values to plot properties."""

    def __init__(
            self,
            prop: str = None,
            mapping: Union[Callable, dict, list] = None,
            data: Iterable = None,
            default: any = None):
        self.prop = prop
        self.default = default
        if data is not None and isinstance(mapping, list):
            try:
                levels = data.unique()
            except AttributeError:
                levels = list(set(data))
            if is_categorical_dtype(data):
                mapping = {key: mapping[value % len(mapping)]
                           for key, value in zip(levels, levels.codes)}
            else:
                mapping = {levels[i]: mapping[i % len(mapping)] for i in range(len(levels))}
        self.mapping = mapping

    def get_props(self, value: any) -> dict:
        """Return the props for a particular value."""
        try:
            props = self.mapping(value)
        except TypeError:
            try:
                props = self.mapping[value]
            except (IndexError, KeyError):
                props = self.default

        if isinstance(props, dict):
            return props
        return {self.prop: props}

    def __getitem__(self, value: any) -> dict:
        return self.get_props(value)


class ColorPropMapper(PropMapper):
    """
    Class for mapping data on to colors.
    """

    def __init__(
            self,
            prop,
            mapping: Union[str, Dict, List],
            data: Iterable = None,
            default: Any = None):

        if isinstance(mapping, matplotlib.colors.Colormap):
            mapping = list(mapping.colors)
        if not isinstance(mapping, list):
            try:
                mapping = list(get_cmap(mapping).colors)
            except ValueError:
                mapping = [mapping]

        super().__init__(prop, mapping=mapping, data=data, default=default)


class IndexPropMapper(PropMapper):
    """
    Class for mapping data on to a sequence of integers.
    """

    def __init__(
            self,
            prop,
            mapping: Union[Dict, List] = None,
            start: int = 0,
            data: Iterable = None,
            default: Any = None):
        mapping = mapping or [start + i for i in range(len(data.unique()))]
        super().__init__(prop, mapping=mapping, data=data, default=default)


def get_prop_mapper(prop, mapping=None, data=None, default=None):
    if prop == 'plot':
        return IndexPropMapper(prop, mapping=mapping, data=data, default=default)
    elif 'color' in prop:
        return ColorPropMapper(prop, mapping=mapping, data=data, default=default)
    return PropMapper(prop, mapping=mapping, data=data, default=default)


def mapping_from_data(data: Iterable, values: Iterable) -> dict:
    """Map categorical data values to prop values."""
    try:
        uniques = list(data.values.categories)
    except AttributeError:
        try:
            uniques = sorted(data.unique())
        except AttributeError:
            uniques = sorted(np.unique(values))
    return {value: unique for value, unique in zip(values, uniques)}


class GroupPropsMapper:
    """Class for managing the mapping of multiple props."""

    def __init__(self, groups):
        self.groups = groups
        self.mappers = OrderedDict({group: [] for group in groups})

    def add_mapper(self, group, mapper):
        self.mappers[group].append(mapper)

    def get_props(self, data, *args, defaults=None, **kwargs):
        props = {}
        group_props = OrderedDict()
        for group, value in data:
            group_props[group] = {**(defaults or {})}
            for mapper in self.mappers[group]:
                group_props[group].update(**mapper.get_props(value, *args, **kwargs))
            props.update(**group_props[group])
        return props, group_props
