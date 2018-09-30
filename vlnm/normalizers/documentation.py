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
        dict(
            columns=document_columns(cls._columns),
            keywords=document_keywords(cls.__name__, cls._keywords)))
    return cls

def document_columns(columns):  ## pylint: disable=unused-argument
    """
    Generate
    """
    docs = '''

    Args:
        foo (int): an integer
    Keyword:
        rename (string):
            A string which will be used to format the output columns.

    '''

    return docs.strip()

def document_keywords(name, keywords):
    """
    Generate keyword documentation.
    """
    docstring = '''
    {} {}
    '''.format(name, keywords)
    return docstring[-1:]
