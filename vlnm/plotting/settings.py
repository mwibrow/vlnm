"""
Settings
~~~~~~~~
"""

import copy
import json
from typing import Union

import pandas as pd


class SettingsEncoder(json.JSONEncoder):
    """Helper class for debugging settings."""

    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.__class__.__name__
        return json.JSONEncoder.default(self, obj)


def state(*args, **kwargs):
    """Helper function to create a dictionary from **args and **kwargs."""
    value = {}
    for arg in args:
        value.update(**arg)
    value.update(**kwargs)
    return value


def deepcopy(src, depth=0):
    """Custom deepcopy."""
    dest = {}
    for key, value in src.items():
        if value is None:
            continue
        if isinstance(value, dict) and depth:
            dest[key] = deepcopy(value, depth - 1)
        elif isinstance(value, pd.DataFrame):
            dest[key] = value
        else:
            dest[key] = copy.deepcopy(value)
    return dest


def deepmerge(lhs, rhs, depth=0):
    """Deep merge settings."""
    dest = lhs.copy()
    for key, value in rhs.items():
        if value is None:
            continue
        if isinstance(value, dict) and depth:
            dest[key] = deepmerge(dest.get(key, {}), value, depth - 1)
        elif isinstance(value, pd.DataFrame):
            dest[key] = value
        else:
            dest[key] = copy.deepcopy(value)
    return dest


class Settings:
    """Container for settings."""

    def __init__(self, *args, **kwargs):
        self.scopes = [[state(*args, **kwargs)]]

    @property
    def stack(self):
        return self.scopes[-1]

    @property
    def state(self):
        return self.stack[-1]

    def push(self, *args, **kwargs):
        """Push settings onto the stack in the current scope."""
        item = deepmerge(self.state, state(*args, **kwargs), depth=1)
        self.stack.append(item)

    def pop(self):
        """Remove the settings last added to the stack."""
        return self.stack.pop()

    def scope(self, *args, **kwargs):
        """Shorthand for begin_scope."""
        return self.begin_scope(*args, **kwargs)

    def begin_scope(self, *args, **kwargs):
        """Begin a new settings scope."""
        self.scopes.append([deepcopy(self.state, depth=1)])
        self.push(*args, **kwargs)
        return self

    def end_scope(self):
        """Restore the last settings scope."""
        return self.scopes.pop()

    def __getitem__(self, keys):
        if isinstance(keys, tuple):
            return {key: self.state.get(key, {}) for key in keys}
        return self.state.get(keys)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        return self.end_scope()

    def __repr__(self):
        return json.dumps(self.scopes, indent=2, cls=SettingsEncoder)
