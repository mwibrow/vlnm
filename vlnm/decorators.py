"""
Decorators.
"""
# pylint: disable=C0103,W0212

import pystache

from vlnm.documentation import document_columns, document_keywords
from vlnm.normalizers import register_normalizer

def DocString(cls):  # pylint: disable=C0103
    """
    Decorator for auto generating docstrings
    """

    cls.__doc__ = pystache.render(
        cls.__doc__,
        dict(
            columns=document_columns(cls._columns),
            keywords=document_keywords(cls.__name__, cls._keywords)))
    return cls

def Register(*aliases):  # pylint: disable=C0103
    """Decorator for registering normalizers."""
    def _decorator(cls):
        register_normalizer(cls, *aliases)
        return cls
    return _decorator

class Parameters:
    """
    Base class for normalizer decorator.
    """
    def __init__(
            self,
            required=None,
            optional=None,
            choice=None,
            returns=None):

        self.required = required or []
        self.choice = choice or {}
        self.optional = optional or []
        self.returns = returns or []

    def as_list(self):
        """
        Return all parameters as a list.
        """
        parameters = []
        parameters.extend(self.required)
        for choices in self.choice.values():
            parameters.extend(choices)
        parameters.extend(self.optional)
        return parameters

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

def Name(name):
    """
    Decorator for adding custom name to a normalizer class.
    """
    def cls_decorator(cls):
        """
        Decorate {cls} with {_name}
        """
        cls._name = name
        return cls
    return cls_decorator
