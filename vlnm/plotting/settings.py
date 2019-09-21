"""
Settings
~~~~~~~~
"""


class Settings:
    """Container for settings."""

    def __init__(self, settings=None):
        self.stack = [settings] if settings else []

    def push(self, setting=None, **settings):
        """Add settings to the stack."""
        if setting:
            self.stack.append(setting)
        if settings:
            self.stack.append(settings)

    def pop(self):
        """Remove settings from the stack."""
        return self.stack.pop()

    def current(self, setting=None):
        """Look at the current value of the stack."""
        settings = {}
        if setting:
            for item in self.stack:
                try:
                    settings.update(**item.get(setting, {}))
                except (AttributeError, TypeError):
                    settings = item.get(setting)
        else:
            for item in self.stack:
                for key, value in item.items():
                    settings[key] = settings.get(key, {})
                    try:
                        settings[key].update(**value)
                    except (AttributeError, TypeError):
                        settings[key] = value

        return settings

    def scope(self, setting=None, **settings):
        """Enter a setting scope."""
        self.push(setting, **settings)
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
