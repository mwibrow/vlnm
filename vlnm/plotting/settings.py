"""
Settings
~~~~~~~~
"""

import json

import pandas as pd


def strip_dict(source, deep=False, ignore=None):
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
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.__class__.__name__
        return json.JSONEncoder.default(self, obj)


class ScopedStack:
    """Class for managing stacks and scopes."""

    def __init__(self):
        self.scopes = [[{}]]

    @property
    def stack(self):
        return self.scopes[-1]

    def push(self, item):
        """Push an item on to the current stack."""
        stack = self.stack

        new = {**stack[-1]}
        new.update(**item)
        self.stack.append(new)

    def peek(self):
        """Peek at the top of the stack."""
        return self.stack[-1]

    def pop(self):
        """Pop and item from the current stack."""
        return self.stack.pop()

    def begin_scope(self):
        """Start a new scope."""
        self.scopes.append([self.peek()])

    def end_scope(self):
        """End a new scope."""
        return self.scopes.pop()

    def __enter__(self):
        self.begin_scope()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        self.end_scope()
        return True

    def __iter__(self):
        for stack in self.scopes:
            for item in stack:
                yield item

    def __repr__(self):
        return json.dumps(self.scopes, cls=SettingsEncoder, indent=2)


class Settings:
    """Container for settings."""

    def __init__(self, *args, **kwargs):
        self.stack = ScopedStack()
        self.push(*args, **kwargs)
        self._current = None

    def push(self, *args, **kwargs):
        """Add settings to the stack."""
        stack = self.stack.peek()
        item = {}
        for arg in args:
            for key, value in arg.items():
                item[key] = stack.get(key, {})
                try:
                    item[key].update(**strip_dict(value))
                except (AttributeError, TypeError):
                    item[key] = arg[key]
        for key, value in kwargs.items():
            item[key] = stack.get(key, {})
            try:
                item[key].update(**strip_dict(kwargs[key]))
            except (AttributeError, TypeError):
                item[key] = kwargs[key]

        self.stack.push(item)

    def pop(self):
        """Remove settings from the stack."""
        self._current = None
        return self.stack.pop()

    def current(self, setting=None):
        """Look at the current value of the stack."""
        settings = {}
        if isinstance(setting, str):
            return self.stack.peek().get(setting)
        stack = self.stack.peek()
        if setting:
            settings = {key: stack.get(key, {}) for key in setting}
        else:
            settings = stack
        return settings or {}

    def scope(self, *args, **kwargs):
        """Enter a setting scope."""
        self.stack.begin_scope()
        self.push(*args, **kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        self.stack.end_scope()
        self._current = None

        return True

    def __getitem__(self, setting):
        return self.current(setting)

    def __repr__(self):
        return self.stack.__repr__()
