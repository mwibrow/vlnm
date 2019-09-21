"""
Settings
~~~~~~~~
"""


class Settings:
    """Container for settings."""

    def __init__(self, settings=None):
        self.stack = [settings] if settings else []

    def push(self, settings=None, **kwargs):
        """Add settings to the stack."""
        if settings:
            self.stack.append(settings)
        if kwargs:
            self.stack.append(kwargs)

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

    def __getitem__(self, setting):
        if isinstance(setting, slice):
            return self.current()
        return self.current(setting)
