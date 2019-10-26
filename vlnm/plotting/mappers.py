"""
    Property mappers module
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from typing import Any, Callable, Iterable, List, Union

from matplotlib.cm import get_cmap
import numpy as np

Primative = Union[int, float, str, bool]


def unique(data: Iterable, sort=True):
    """Get unique data values."""
    try:
        uniques = list(data.values.categories)
    except AttributeError:
        try:
            uniques = sorted(data.unique()) if sort else list(data.unique())
        except AttributeError:
            uniques = sorted(np.unique(data)) if sort else list(np.unique(data))
    return uniques


class Mapper:
    """Class for mapping data values onto property values."""

    def __init__(
            self,
            values: Union[dict, list, Primative, Callable, 'Mapper'],
            cycle: bool = False,
            default: bool = None):
        if isinstance(values, Mapper):
            self.values = values.values
            self.cycle = values.cycle
            self.default = values.default
            self.indexer = {}
        else:
            self.values = values
            self.cycle = cycle
            self.default = default
            self.indexer = {}

    def get_value(self, data: Any, *args, **kwargs) -> Any:
        """Return a property value for a data value."""
        try:
            return self.values(data, *args, **kwargs)
        except TypeError:  # Not a function
            try:
                return self.values.get(data, self.default)
            except AttributeError:  # Not a dictionary
                if isinstance(self.values, list):
                    try:
                        if self.cycle:
                            data = data % len(self.values)
                        try:
                            return self.values[data]
                        except IndexError:
                            return self.default
                    except TypeError:
                        index = self.indexer.get(data, len(self.indexer))
                        self.indexer[data] = index
                        return self.get_value(index, *args, **kwargs)
                return data

    def __getitem__(self, data):
        return self.get_value(data)


def prop_mapper(prop: str, value: any, cycle: bool = True, default: any = None) -> Mapper:
    """Factory method for Mapper class."""
    if 'color' in prop:
        return color_mapper(value, cycle=cycle, default=default)
    return Mapper(value, cycle=cycle, default=default)


def color_mapper(value: any, cycle: bool = False, default: any = None) -> Mapper:
    """Factory method for color mappings."""
    try:
        values = list(value.colors)
    except AttributeError:  # Not a Colormap
        try:
            values = list(get_cmap(value).colors)
        except (TypeError, AttributeError, ValueError):  # Not a Colormap name
            values = value
    return Mapper(values, cycle=cycle, default=default)


class PropsMapper:
    """Class for managing the mapping of data values onto multiple properties."""

    def __init__(self, **kwargs):
        self.mappers = {}
        self.update(**kwargs)

    def enable_cycles(self, enable: bool = True, prop: str = None):
        """Enable cycles on mappers in this instance."""
        if prop:
            self.mappers[prop].cycle = enable
        else:
            for prp in self.mappers:
                self.mappers[prp].cycle = enable

    def get_props(self, value: any, *args, **kwargs) -> dict:
        """Return all props for a data value."""
        props = {}
        for prp in self.mappers:
            props.update(**self.get_prop(prp, value, *args, **kwargs))
        return props

    def get_prop(self, prop: str, value: any, *args, **kwargs):
        """Return a single prop for a data value."""
        mapper = self.mappers[prop]
        props = mapper.get_value(value, *args, **kwargs)
        if isinstance(props, dict):
            return props
        return {prop: props}

    def update(self, *args, **kwargs):
        for arg in args:
            self.mappers.update(**arg)
        self.mappers.update(**{key: Mapper(value) for key, value in kwargs.items()})


class GroupPropsMapper:
    """Class for managing the mapping of data groups/columns onto property values.

    """

    def __init__(self, groups: List[str]):
        self.groups = {group: PropsMapper() for group in groups}

    def add_mapper(
            self,
            group: str,
            prop: str,
            mapper: Mapper):
        """Add a prop mapping for a data group."""
        self.groups[group].update({prop: mapper})

    def add_prop_mapper(
            self,
            group: str,
            prop: str,
            values: Mapper,
            **kwargs):
        """Add a factory prop mapping for a data group."""
        self.groups[group].update({prop: prop_mapper(prop, values, **kwargs)})

    def get_props(self, groups: Union[List, str], values: any, *args, **kwargs) -> dict:
        """
        Return property values for each data group
        """
        if isinstance(groups, dict):
            iterator = groups.items()
        else:
            iterator = zip(groups, values)
        return {group: self.groups[group].get_props(value, *args, **kwargs)
                for group, value in iterator}
