"""
Misc. utilities.
"""

def items_to_str(items, sep=',', junction=None, oxford=False, quote=None):
    """
    Convert a list of items to a stringified list.
    """
    if not items:
        return ''
    sorted_items = sorted(items)
    quote = quote or ''
    if len(sorted_items) == 2:
        return '{}{}{}{}'.format(
            '{}{}{}'.format(quote, sorted_items[0], quote),
            sep if oxford or not junction else '',
            ' {} '.format(junction) if junction else ' ',
            '{}{}{}'.format(quote, sorted_items[1], quote))
    elif len(items) == 1:
        return '{}{}{}'.format(quote, sorted_items[0], quote)
    return '{}{} {}'.format(
        '{}{}{}'.format(quote, sorted_items[0], quote),
        sep,
        items_to_str(
            sorted_items[1:],
            sep=sep,
            junction=junction,
            oxford=oxford,
            quote=quote))

def merge_columns(column_specs, kwargs):
    """
    Merge required columns with given columns
    """
    for spec in column_specs:
        column = column_specs[spec]
        try:
            if column not in kwargs:
                kwargs[column] = column
        except TypeError:
            if not any(item in kwargs for item in column):
                for item in column:
                    kwargs[item] = item
    return kwargs

def check_required_columns(column_specs, kwargs, replace=True):
    for spec in column_specs:
        column = column_specs[spec]
        try:
            if column not in kwargs:
                if replace:
                    kwargs[column] = column
                else:
                    raise ValueError()
        except TypeError:
            if not any(item in kwargs for item in column):
                if replace:
                    for item in column:
                        kwargs[item] = item
                else:
                    raise ValueError()
    return False




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

# def check_required_kwargs(kwargs, required):
#     """
#     Check required keyword arguments are present.
#     """
#     required = required or []
#     for key in required:
#         if not key in kwargs:
#             return key
#     return None

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
