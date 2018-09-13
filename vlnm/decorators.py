"""
Class decorators for normalizers.
"""
# pylint: disable=protected-access, invalid-name, too-few-public-methods

def DocString(cls):
    """
    Decorator for auto generating docstrings
    """
    return cls

class Parameters:
    """
    Base class for normalizer decorator.
    """
    def __init__(
            self,
            required=None,
            optional=None,
            choice=None):

        self.required = required
        self.choice = choice
        self.optional = optional

def Columns(**columns):
    """
    Decorator for specifying require and optional data frame columns.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_columns}
        """
        cls._columns = Parameters(**columns)
        return cls
    return cls_decorator

def Keywords(**keywords):
    """
    Decorator for specifying required and optional normalizer keywords.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_keywords}
        """
        cls._keywords = Parameters(**keywords)
        return cls
    return cls_decorator

def Returns(**returns):
    """
    Decorator for specifying columns returned by a normalizer.
    """

    def cls_decorator(cls):
        """
        Decorate {cls} with {_returns}
        """
        cls._returns = returns
    return cls_decorator
