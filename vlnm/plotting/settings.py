"""
Settings
~~~~~~~~
"""

import copy
import json
from typing import Union

import pandas as pd


def strip_dict(source, deep=False, ignore=None):
    """Strip keys from a dictionary."""
    if not source:
        return source
    ignore = ignore or [None]
    destination = {}
    for key, value in source.items():
        if not any(value is i for i in ignore):
            if isinstance(value, dict) and deep:
                destination[key] = strip_dict(value, deep=deep, ignore=ignore)
            else:
                destination[key] = value
    return destination


class SettingsEncoder(json.JSONEncoder):
    """Helper class for debugging settings."""

    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.__class__.__name__
        return json.JSONEncoder.default(self, obj)


def state(*args, **kwargs):
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
        item = deepmerge(self.state, state(*args, **kwargs), depth=1)
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def begin_scope(self, *args, **kwargs):
        self.scopes.append([deepcopy(self.state, depth=1)])
        self.push(*args, **kwargs)

    def end_scope(self):
        return self.scopes.pop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        return True
