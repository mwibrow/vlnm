"""
    Plotting utilities
    ~~~~~~~~~~~~~~~~~~

"""
from typing import Dict


def _strip_none(dct):
    return {key: value for key, value in dct.items() if value is not None}


class Context(dict):
    r"""Wrapper around dictionary class which ignores ``None`` values.

    Parameters
    ----------
    \*args: :obj:`Context`
        One or more :class:`.Context` instances.

    \**kwargs:
        Keyword arguments.


    """

    def __init__(self, *args, **kwargs):
        context = {}
        for arg in args:
            context.update(**_strip_none(arg))
        context.update(**_strip_none(kwargs))
        super().__init__(**context)

    def __setitem__(self, key, value):
        if value is not None:
            super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        r"""Update the Context instance.

        Parameters
        ----------
        \*args: :obj:`Context`
            One or more :class:`.Context` instances.

        \**kwargs:
            Keyword arguments.
        """
        for arg in args:
            super().update(_strip_none(arg))
        kwargs = _strip_none(kwargs)
        super().update(**kwargs)

    def merge(self, other):
        return Context(merge(self, other))

    def filter_bys(self):
        rest = self.copy()
        context = {}
        for key, value in self:
            if key.endswith('_by'):
                prop = key[:-3]
                context[key] = value
                context[prop] = self.get(prop)
                del rest[key]
                del rest[prop]

        return context, rest


def merge(this: Dict, that: Dict) -> Dict:
    """Merge dictionaries recursively.

    Parameters
    ----------
    this:
        Dictionary containing old keys.
    that:
        Dictionary containing new keys.

    Returns
    -------
    :

    """
    merged = this.copy()
    for key, value in that.items():
        if key in merged:
            _this, _that = merged[key], value
            if isinstance(_this, dict) and isinstance(_that, dict):
                merged[key] = merge(_this, _that)
            else:
                merged[key] = _that
        else:
            merged[key] = value
    return merged
