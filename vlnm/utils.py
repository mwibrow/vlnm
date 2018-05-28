"""
Misc. utilities.
"""


def flatten(items):
    """
    Flatten a list of lists.
    """
    if items == []:
        return items
    if isinstance(items, list):
        flattend = []
        for item in items:
            flattend.extend(flatten(item))
        return flattend
    return [items]

def str_or_list(value):
    """
    String to list of string.
    """
    if isinstance(value, list):
        return value
    return [value]

def check_required_kwargs(kwargs, required):
    """
    Check required keyword arguments are present.
    """
    required = required or []
    for key in required:
        if not key in kwargs:
            return key
    return None

def check_one_from_kwargs(kwargs, one_from):
    """
    Check at least one-from keyword arguments is present.
    """
    for items in one_from:
        for item in items:
            if item in kwargs:
                break
        else:
            if one_from:
                return one_from
    return None

def check_data_frame_columns(df, columns):
    """
    Check data frame contains columns.
    """
    for column in columns:
        if not column in df.columns:
            return column
    return None
