"""
    Property mappers module
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from typing import Any, Dict, Iterable, List, Union

from matplotlib.cm import get_cmap
import matplotlib.colors
from pandas.api.types import is_categorical_dtype


class PropMapper:
    """
    Class for mapping data values for properties.

    Parameters
    ----------
    prop:
        Property name
    mapping:
        Mapping between data values and property values or a list of property values.
    data:
        Data values used to create dictionary mapping.
    default:
        Default property value returned if data-value is not in mapping.

    """

    def __init__(
            self,
            prop: str,
            mapping: Union[Dict, List],
            data: Iterable = None,
            default: Any = None):
        self.prop = prop
        self.default = default

        if isinstance(mapping, list):
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

    def get_props(self, domain: Any) -> Any:
        value = self.mapping.get(domain, self.default) if self.default else self.mapping[domain]
        if isinstance(value, dict):
            return value
        return {self.prop: value}

    def __getitem__(self, domain: Any):
        return self.get_value(domain)


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


def get_prop_mapper(prop, mapping=None, data=None):
    if prop == 'plot':
        return IndexPropMapper(prop, mapping=mapping, data=data)
    elif 'color' in prop:
        return ColorPropMapper(prop, mapping=mapping, data=data)
    return PropMapper(prop, mapping=mapping, data=data)
