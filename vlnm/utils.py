"""
Misc. utilities.
"""
import itertools

def flatten(items):
    """
    Flatten a list of lists.
    """
    return [item for item in itertools.chain.from_iterable(items) if item]

def str_or_list(value):
    """
    String to list of string.
    """
    if isinstance(value, list):
        return value
    return [value]
