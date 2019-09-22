"""
Settings
~~~~~~~~
"""


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


class Settings:
    """Container for settings."""

    def __init__(self, settings=None):
        self.stack = [settings] if settings else []

    def push(self, *args, **kwargs):
        """Add settings to the stack."""
        settings = {}
        for arg in args:
            settings.update(**arg)
        settings.update(**kwargs)
        self.stack.append(settings)

    def pop(self):
        """Remove settings from the stack."""
        return self.stack.pop()

    def current(self, setting=None):
        """Look at the current value of the stack."""
        settings = {}
        if setting:
            for item in self.stack:
                value = item.get(setting)
                if isinstance(value, dict):
                    settings.update(**strip_dict(value))
                else:
                    settings = value
        else:
            for item in self.stack:
                for key, value in item.items():
                    settings[key] = settings.get(key, {})
                    try:
                        settings[key].update(**strip_dict(value))
                    except (AttributeError, TypeError):
                        settings[key] = value

        return settings

    def scope(self, *args, **kwargs):
        """Enter a setting scope."""
        self.push(*args, **kwargs)
        return self

    def end_scope(self):
        """Exit a setting scope."""
        self.pop()

    def __getitem__(self, setting):
        if isinstance(setting, slice):
            return self.current()
        return self.current(setting)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            return False
        return self.end_scope()
