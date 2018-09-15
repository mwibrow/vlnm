"""
Module for generating docstrings
"""
# pylint: disable=protected-access, invalid-name, too-few-public-methods
import pystache

def DocString(cls):
    """
    Decorator for auto generating docstrings
    """

    cls.__doc__ = pystache.render(
        cls.__doc__,
        dict(columns=document_columns(cls._columns)))
    return cls

def document_columns(columns):
    """
    Generate
    """
    docs = ''

    return docs

